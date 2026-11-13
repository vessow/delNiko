import sys
from pathlib import Path
import flet as ft
from tools import ToolViews

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))


class DelNikoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "delNiko"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window.width = 900
        self.page.window.height = 580
        self.page.window.icon = str(BASE_DIR / "assets" / "icon.ico")
        self.page.padding = 0

        self.views = ToolViews(self.page, self.wrap_tool_view, self.notify)

        self.tools = [
            ("Password Gen", ft.Icons.LOCK_OUTLINE, "#4F46E5", self.views.password_gen),
            ("Auto Clicker", ft.Icons.MOUSE_OUTLINED, "#0EA5E9", self.views.auto_clicker),
            ("Shutdown Timer", ft.Icons.TIMER_OUTLINED, "#EC4899", self.views.shutdown_timer),
            ("QR Generator", ft.Icons.QR_CODE_2, "#10B981", self.views.qr_gen),
            ("Temp Cleaner", ft.Icons.CLEANING_SERVICES, "#F59E0B", self.views.temp_cleaner),
            ("Quick Notes", ft.Icons.EDIT_NOTE, "#8B5CF6", self.views.quick_notes),
            ("Net Ping", ft.Icons.NETWORK_CHECK, "#06B6D4", self.views.net_ping),
            ("Img Converter", ft.Icons.IMAGE_OUTLINED, "#F43F5E", self.views.img_converter),
            ("File Sorter", ft.Icons.FOLDER_SPECIAL, "#14B8A6", self.views.file_sorter),
            ("Unit Calc", ft.Icons.CALCULATE_OUTLINED, "#6366F1", self.views.unit_calc),
        ]

        self.body_container = ft.Container(expand=True)
        self.setup_layout()
        self.show_home()

    def notify(self, text: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(text))
        self.page.snack_bar.open = True
        self.page.update()

    def setup_layout(self):
        bg = ft.Container(
            image=ft.DecorationImage(
                src="/bg.jpg",
                fit=ft.BoxFit.COVER,
            ),
            expand=True,
        )

        overlay = ft.Container(
            bgcolor=ft.Colors.with_opacity(0.35, "black"),
            expand=True,
        )

        main_layer = ft.Container(
            padding=ft.Padding(30, 30, 30, 15),
            content=self.body_container,
            expand=True,
        )

        self.page.add(ft.Stack([bg, overlay, main_layer], expand=True))

    def show_home(self, e=None):
        self.views.clicker_running = False
        grid = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=160,
            child_aspect_ratio=1.1,
            spacing=15,
            run_spacing=15,
        )

        for title, icon, color, action in self.tools:
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color="white", size=28),
                            bgcolor=color,
                            padding=10,
                            border_radius=12,
                        ),
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                bgcolor=ft.Colors.with_opacity(0.65, "#14161D"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
                border_radius=16,
                padding=10,
                ink=True,
                on_click=lambda e, fn=action: fn(),
            )
            grid.controls.append(card)

        footer = ft.Container(
            content=ft.Text(
                "made by vverg. t.me/vessqwq",
                size=12,
                color=ft.Colors.with_opacity(0.6, "white"),
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding(0, 8, 0, 0),
        )

        self.body_container.content = ft.Column(
            [
                ft.Text("delNiko", size=32, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Select utility", size=14, color="#E5E7EB"),
                ft.Divider(height=10, color="transparent"),
                grid,
                footer,
            ],
            expand=True,
        )
        self.page.update()

    def wrap_tool_view(self, title: str, tool_controls: list):
        header = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color="white",
                    on_click=self.show_home,
                ),
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color="white"),
            ],
            spacing=10,
        )

        panel = ft.Container(
            content=ft.Column(
                [header, ft.Divider(height=10, color="transparent"), *tool_controls],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=ft.Colors.with_opacity(0.78, "#14161D"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
            border_radius=16,
            padding=25,
            expand=True,
        )

        self.body_container.content = panel
        self.page.update()


def main(page: ft.Page):
    DelNikoApp(page)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(BASE_DIR / "assets"))