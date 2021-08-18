import math

import demo.resources
from PySide6 import QtCore, QtWidgets, QtGui
from PyQuotient import Quotient
from demo.accountregistry import AccountRegistry
from demo.chatroomwidget import ChatRoomWidget
from demo.logindialog import LoginDialog
from demo.roomlistdock import RoomListDock
from demo.pyquaternionroom import PyquaternionRoom
from __feature__ import snake_case, true_property


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.login_dialog = None
        self.connection_menu = None
        self.logout_menu = None
        # FIXME: This will be a problem when we get ability to show
        # several rooms at once.
        self.current_room = None

        self.account_registry = AccountRegistry()
        self.room_list_dock = RoomListDock(self)
        self.room_list_dock.roomSelected.connect(self.select_room)
        self.add_dock_widget(QtCore.Qt.LeftDockWidgetArea, self.room_list_dock)

        self.chat_room_widget = ChatRoomWidget(self)
        self.chat_room_widget.showStatusMessage.connect(lambda x = '': self.status_bar().show_message(x))
        self.set_central_widget(self.chat_room_widget)

        self.create_menu()
        # Only GUI, account settings will be loaded in invoke_login
        self.load_settings()

        timer = QtCore.QTimer(self)
        timer.single_shot = True
        timer.timeout.connect(self.invoke_login)
        timer.start(0)
    
    def __del__(self):
        self.save_settings()
    
    def load_settings(self):
        sg = Quotient.SettingsGroup("UI/MainWindow")
        # TODO: fix rect value, is None
        # if sg.contains("normal_geometry"):
        #     self.geometry = sg.value("normal_geometry")
        if sg.value("maximized"):

            self.show_maximized()
        # TODO: fix value, is None
        # if sg.contains("window_parts_state"):
        #     self.restore_state(sg.value("window_parts_state"))
    
    def save_settings(self):
        sg = Quotient.SettingsGroup("UI/MainWindow")
        sg.set_value("normal_geometry", self.normal_geometry)
        sg.set_value("maximized", self.maximized)
        sg.set_value("window_parts_state", self.save_state())
        sg.sync()

    @QtCore.Slot()
    def invoke_login(self):
        accounts = Quotient.SettingsGroup("Accounts").child_groups()
        auto_logged_in = False
        for account_id in accounts:
            account = Quotient.AccountSettings()
            if account.homeserver:
                access_token = self.load_access_token(account)
    
    def load_access_token(self, account: Quotient.AccountSettings):
        ...

    @QtCore.Slot()
    def open_login_window(self):
        self.login_dialog = LoginDialog('Login', self)
        self.login_dialog.open()

        self.login_dialog.accepted.connect(self.on_login_dialog_accepted)
    
    @QtCore.Slot()
    def on_login_dialog_accepted(self):
        connection = self.login_dialog.release_connection()
        device_name = self.login_dialog.device_name

        self.add_connection(connection, device_name)

    @QtCore.Slot(Quotient.Connection)
    def logout(self, connection: Quotient.Connection):
        connection.logout()

    @QtCore.Slot()
    def quit(self):
        QtWidgets.QApplication.quit()

    def add_connection(self, connection: Quotient.Connection, device_name: str):
        connection.lazy_loading = True
        self.account_registry.add(connection)
        self.room_list_dock.add_connection(connection)
        connection.syncLoop(30000)

        logout_action = self.logout_menu.add_action(connection.local_user_id, lambda: self.logout(connection))
        connection.destroyed.connect(lambda: self.logout_menu.remove_action(logout_action))
        connection.syncDone.connect(lambda: self.on_sync_done(connection))
        connection.loggedOut.connect(lambda: self.on_logged_out(connection))
        connection.networkError.connect(lambda: self.on_network_error(connection))
        connection.syncError.connect(lambda message, details: self.on_sync_error(connection, message, details))
        connection.requestFailed.connect(self.on_request_failed)
        connection.loginError.connect(lambda message: self.on_login_error(connection, message))
    
    @QtCore.Slot(Quotient.Connection)
    @QtCore.Slot(Quotient.Connection, int)
    def on_sync_done(self, connection: Quotient.Connection, counter = 0):
        if counter == 0:
            self.first_sync_over(connection)
            self.status_bar().show_message(f'First sync completed for {connection.local_user_id}', 3000)

        counter += 1
        # Borrowed the logic from Quiark's code in Tensor to cache not too
        # aggressively and not on the first sync.
        if counter % 17 == 2:
            connection.save_state()

    def first_sync_over(self, connection: Quotient.Connection):
        # will be needed later after implementation of account registry
        ...

    def drop_connection(self, connection: Quotient.Connection):
        # will be needed later after implementation of account registry
        ...

    def on_network_error(self, connection: Quotient.Connection):
        timer = QtCore.QTimer(self)
        timer.start(1000)
        self.show_millis_to_recon(connection)
        timer.timeout.connect(lambda: self.on_reconnection_timer_timeout(connection))

    def on_sync_error(self, connection: Quotient.Connection, message: str, details: str):
        message_box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            'Sync failed',
            f'The last sync has failed with error: {message}',
            QtWidgets.QMessageBox.Retry|QtWidgets.QMessageBox.Cancel,
            self
        )
        message_box.text_format = QtCore.Qt.PlainText
        message_box.default_button = QtWidgets.QMessageBox.Retry
        message_box.informative_text = (
            "Clicking 'Retry' will attempt to resume synchronisation;\n"
            "Clicking 'Cancel' will stop further synchronisation of this "
            "account until logout or Quaternion restart."
        )
        message_box.detailed_text = details
        if message_box.exec() == QtWidgets.QMessageBox.Retry:
            connection.syncLoop(30000)
    
    def on_request_failed(self, job: Quotient.BaseJob):
        if job.is_background:
            return
        
        message = (
            "Before this server can process your information, you have"
            " to agree with its terms and conditions; please click the"
            " button below to open the web page where you can do that"
        )
        if not job.is_background:
            message = job.error_string
        
        message_box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            job.status_caption,
            message,
            QtWidgets.QMessageBox.Close,
            self
        )
        message_box.text_format = QtCore.Qt.RichText
        message_box.detailed_text = f'Request URL: {job.request_url.to_display_string()}\nResponse:\n{job.raw_data_sample()}'
        open_url_button = None
        if len(job.error_url) == 0:
            message_box.default_button = QtWidgets.QMessageBox.Close
        else:
            open_url_button = message_box.add_button('Open web page', QtWidgets.QMessageBox.ActionRole)
            open_url_button.defaut = True
        
        message_box.exec()
        if message_box.clicked_button == open_url_button:
            QtGui.QDesktopServices.open_url(job.error_url)

    def on_login_error(self, connection: Quotient.Connection, message: str):
        connection.stopSync()
        # Security over convenience: before allowing back in, remove
        # the connection from the UI
        connection.loggedOut.emit() # Short circuit login error to logged-out event
        # TODO: show relogin window: showLoginWindow(message, c->userId());
    
    def on_reconnection_timer_timeout(self, connection: Quotient.Connection):
        if connection.millis_to_reconnect > 0:
            self.show_millis_to_recon(connection)
        else:
            self.status_bar().show_message('Reconnecting...', 5000)

    def on_logged_out(self, connection: Quotient.Connection):
        self.status_bar().show_message(f'Logged out as {connection.local_user_id}', 3000)
        self.account_registry.drop(connection)
        self.drop_connection(connection)

    def create_menu(self):
        self.connection_menu = self.menu_bar().add_menu('Accounts')
        self.connection_menu.add_action('Login', self.open_login_window)
        self.connection_menu.add_separator()
        self.logout_menu = self.connection_menu.add_menu('Logout')
        self.connection_menu.add_action('Quit', self.quit)

    def show_millis_to_recon(self, connection: Quotient.Connection):
        """
        TODO: when there are several connections and they are failing, these
        notifications render a mess, fighting for the same status bar. Either
        switch to a set of icons in the status bar or find a stacking
        notifications engine already instead of the status bar.
        """
        self.status_bar().show_message('Couldn\'t connect to the server as {user}; will retry within {seconds} seconds'.format(
            user=connection.local_user_id, seconds=math.ceil(connection.millis_to_reconnect)
        ))
    
    @QtCore.Slot(PyquaternionRoom)
    def select_room(self, room: PyquaternionRoom) -> None:
        if room is not None:
            print(f'Opening room {room.object_name()}')
        elif self.current_room is not None:
            print(f'Closing room {self.current_room.object_name()}')
        
        if self.current_room is not None:
            self.current_room.displaynameChanged.disconnect(self.current_room_displayname_changed)
        
        self.current_room = room
        new_window_title = ''
        if self.current_room:
            new_window_title = self.current_room.display_name()
            self.current_room.displaynameChanged.connect(self.current_room_displayname_changed)
        
        self.window_title = new_window_title
        self.room_list_dock.set_selected_room(self.current_room)

        if room is not None and not self.is_active_window():
            self.show()
            self.activate_window()
    
    @QtCore.Slot()
    def current_room_displayname_changed(self):
        self.window_title = self.current_room.displayName()
