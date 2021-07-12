import math

from PySide6 import QtCore, QtWidgets, QtGui
from __feature__ import snake_case, true_property

from PyQuotient import Quotient
from demo.logindialog import LoginDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.text_label = QtWidgets.QLabel("Welcome to PyQuotient demo!")
        self.login_dialog = None
        self.connection_menu = None
        self.logout_menu = None

        self.set_central_widget(self.text_label)

        self.create_menu()

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