import psutil
import socket

from rich.markdown import Markdown
from textual.containers import Container, Horizontal
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Static, Button
from textual.binding import Binding


WELCOME_MD = """\
## Run with sudo\
"""


class Welcome(Container):
    def compose(self) -> ComposeResult:
        yield Static(Markdown(WELCOME_MD))
        yield Button("ok", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.exit()


class TableApp(App):
    TITLE = "Listening Ports"
    BINDINGS = [
        Binding("ctrl+c,ctrl+q", "app.quit", "Quit", show=True),
    ]
    CSS = '''\
TableApp.-hidden {
    offset-x: -100%;
}
Welcome {
    layer: overlay;
}
Welcome.-hidden {
    offset-x: -100%;
}
Welcome Button {
    align: center middle;
    width: 100%;
    margin-top: 1;
}
'''

    def compose(self) -> ComposeResult:
        yield Container(
            DataTable(),
            Welcome(),
            Footer()
        )

    def on_mount(self) -> None:
        try:
            connections = tcp_ports()
            table = self.query_one(DataTable)
            table.add_column('PID', width=5)
            table.add_column('exe', width=80)
            table.add_column('name', width=30)
            table.add_column('ip', width=15)
            table.add_column('port', width=5)
            for c in connections:
                (ip, port) = c.laddr
                p = psutil.Process(c.pid)
                table.add_row(str(p.pid), p.exe(), p.name(), ip, str(port))
            self.query_one(Welcome).add_class('-hidden')
        except:
            pass

    def show_error(self, visible: bool):
        welcome = self.query_one(Welcome)
        if visible:
            welcome.remove_class('-hidden')
        else:
            welcome.add_class('-hidden')

    def show_table(self, visible: bool):
        table = self.query_one(DataTable)
        table.add_column('PID', width=5)
        table.add_column('exe', width=80)
        table.add_column('name', width=30)
        table.add_column('ip', width=15)
        table.add_column('port', width=5)
        for c in tcp_ports():
            (ip, port) = c.laddr
            p = psutil.Process(c.pid)
            table.add_row(str(p.pid), p.exe(), p.name(), ip, str(port))


def tcp_ports():
    connections = psutil.net_connections('inet')
    tcp_connections = []
    for c in connections:
        (ip, port) = c.laddr
        if ip == '0.0.0.0' or ip == '::':
            if c.type == socket.SOCK_STREAM and c.status == psutil.CONN_LISTEN:
                tcp_connections.append(c)
    return tcp_connections
