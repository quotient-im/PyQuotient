from PySide6 import QtCore, QtWidgets, QtGui
from __feature__ import snake_case, true_property

from PyQuotient import Quotient
from PyQuotient.qt_connection_util import connect_single_shot
from .dialog import Dialog


class LoginDialog(Dialog):
    def __init__(self, status_message: str, parent=None):
        super().__init__('Login', parent, Dialog.UseStatusLine.STATUS_LINE, 'Login', Dialog.no_extra_buttons)
        # connection
        self.connection = Quotient.Connection()
        self.connection.connected.connect(self.accept)
        self.connection.loginError.connect(self.on_login_error)
        self.connection.homeserverChanged.connect(self.on_conn_homeserver_changed)
        self.connection.loginFlowsChanged.connect(self.on_conn_login_flows_changed)
        self.connection.resolveError.connect(self.on_conn_resolve_error)

        # widgets
        self.user_edit = QtWidgets.QLineEdit(self)
        self.user_edit.editingFinished.connect(self.on_user_edit_editing_finished)
        self.password_edit = QtWidgets.QLineEdit(self)
        self.password_edit.echo_mode = QtWidgets.QLineEdit.Password
        self.initial_device_name = QtWidgets.QLineEdit(self)
        self.server_edit = QtWidgets.QLineEdit(self)
        self.server_edit.text = 'https://matrix.org'
        self.server_edit.editingFinished.connect(self.on_server_edit_editing_finished)
        self.save_token_check = QtWidgets.QCheckBox('Stay logged in', self)

        # buttons
        # This button is only shown when BOTH password auth and SSO are available
        # If only one flow is there, the "Login" button text is changed instead
        self.sso_button = self.button_box.add_button('Login with SSO', QtWidgets.QDialogButtonBox.AcceptRole)
        self.sso_button.clicked.connect(self.login_with_sso)
        self.sso_button.hidden = True

        # layout
        self.form_layout = QtWidgets.QFormLayout()
        self.add_layout(self.form_layout)
        self.form_layout.add_row('Matrix ID', self.user_edit)
        self.form_layout.add_row('Password', self.password_edit)
        self.form_layout.add_row('Device name', self.initial_device_name)
        self.form_layout.add_row('Connect to server', self.server_edit)
        self.form_layout.add_row(self.save_token_check)

        # fill default data in connection
        self.connection.homeserver = self.server_edit.text

    # properties
    @property
    def device_name(self) -> str:
        return self.initial_device_name.text
    
    @property
    def keep_logged_in(self) -> bool:
        return self.save_token_check.checked

    # methods & slots
    def release_connection(self):
        return self.connection
    
    def apply(self):
        url = QtCore.QUrl.from_user_input(self.server_edit.text)
        if not self.server_edit.text == '' and not self.server_edit.text.startswith('http:'):
            url.set_scheme('https')

        if self.connection.homeserver == url and len(self.connection.login_flows) == 0:
            self.login_with_best_flow()
        elif not url.is_valid():
            self.apply_failed('The server URL doesn\'t look valid')
        else:
            self.connection.homeserver = url
            connect_single_shot(self.connection.loginFlowsChanged, self.on_apply_login_flows_changed)

    def on_apply_login_flows_changed(self):
        print('Received login flows, trying to login')
        self.login_with_best_flow()


    def login_with_best_flow(self):
        if len(self.connection.login_flows) == 0 or self.connection.supports_password_auth:
            self.login_with_password()
        elif self.connection.supports_sso:
            self.login_with_sso()
        else:
            self.apply_failed('No supported login flows')

    @QtCore.Slot()
    def login_with_password(self):
        self.connection.loginWithPassword(self.user_edit.text, self.password_edit.text, self.initial_device_name.text, '')
    
    @QtCore.Slot()
    def login_with_sso(self):
        sso_session = self.connection.prepare_for_sso(self.initial_device_name.text)
        if not QtGui.QDesktopServices.open_url(sso_session.sso_url):
            instruction_box = Dialog('Single sign-on', self, add_buttons=QtWidgets.QDialogButtonBox.NoButton)
            label = QtWidgets.QLabel(('Quaternion couldn\'t automatically open the single sign-on URL. '
                                      'Please copy and paste it to the right application (usually '
                                      'a web browser):'))
            url_box = QtWidgets.QLineEdit(sso_session.sso_url.to_string())
            url_box.read_only = True
            label_2 = QtWidgets.QLabel(('After authentication, the browser will follow '
                                        'the temporary local address setup by Quaternion '
                                        'to conclude the login sequence.'))

            instruction_box.add_widget(label)
            instruction_box.add_widget(url_box)
            instruction_box.add_widget(label_2)

            instruction_box.open()


    @QtCore.Slot(str, str)
    def on_login_error(self, message: str, details: str):
        print('login error: ', message, details)
        self.status_message = message

        self.apply_failed(message)

    @QtCore.Slot(QtCore.QUrl)
    def on_conn_homeserver_changed(self, url: QtCore.QUrl):
        self.server_edit.text = str(url.to_string())
        if url.is_valid():
            self.status_message = 'Getting supported login flows...'

        self.buttons.button(QtWidgets.QDialogButtonBox.Ok).enabled = url.is_valid()

    @QtCore.Slot()
    def on_conn_login_flows_changed(self):
        can_use_sso = self.connection.supports_sso
        can_use_password = self.connection.supports_password_auth
        self.sso_button.visible = can_use_sso and can_use_password
        ok_button_text = 'Login'
        if can_use_sso and not can_use_password:
            ok_button_text = 'Login with SSO'
        self.buttons.button(QtWidgets.QDialogButtonBox.Ok).text = ok_button_text

        self.server_edit.text = self.connection.homeserver.to_string()
        status_message = 'Could not connect to the homeserver'
        if self.connection.is_usable:
            status_message = 'The homeserver is available'
        self.status_message = status_message
        self.buttons.button(QtWidgets.QDialogButtonBox.Ok).enabled = self.connection.is_usable

    @QtCore.Slot(str)
    def on_conn_resolve_error(self, message: str):
        print('Resolve error')
        self.server_edit.clear()
        self.status_message = message

    @QtCore.Slot()
    def on_user_edit_editing_finished(self):
        user_id = self.user_edit.text
        if user_id.startswith('@') and not ':' in user_id:
            self.status_message = 'Resolving the homeserver...'
            self.server_edit.clear()
            self.buttons.button(QtWidgets.QDialogButtonBox.Ok).enabled = False
            self.connection.resolve_server(user_id)

    @QtCore.Slot(str)
    def on_server_edit_editing_finished(self, server: str):
        hs_url = QtCore.QUrl(server)
        if hs_url.is_valid():
            self.connection.homerserver = server
            self.buttons.button(QtWidgets.QDialogButtonBox.Ok).enabled = True
        else:
            self.status_message = 'The server URL doesn\'t look valid'
            self.buttons.button(QtWidgets.QDialogButtonBox.Ok).enabled = False

    @QtCore.Slot()
    def on_conn_connected(self):
        self.accept()
