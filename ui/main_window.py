# ui/main_window.py
from PySide6 import QtCore, QtWidgets, QtGui
from core.engine import Engine
from .overlay import Overlay

class UiBridge(QtCore.QObject):
    log = QtCore.Signal(str)
    status = QtCore.Signal(bool)
    overlay = QtCore.Signal(str, str)
    snapshot = QtCore.Signal(list) # 补回快照信号

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GW2 Director Pro (PySide6 Ultimate)")
        self.resize(1100, 800)
        
        self.bridge = UiBridge()
        self.bridge.log.connect(self._append_log)
        self.bridge.status.connect(self._set_status)
        self.bridge.overlay.connect(self._set_overlay)
        # 即使这里没写复杂的快照渲染，保留接口未来也好扩展
        
        self.engine = Engine(
            on_log=self.bridge.log.emit,
            on_status=self.bridge.status.emit,
            on_overlay=self.bridge.overlay.emit,
            on_snapshot=self.bridge.snapshot.emit
        )

        self.overlay = Overlay()
        self.overlay.show()
        self._init_ui()
        
        # 启动键盘监听线程 (比 QTimer 更强)
        self._key_thread = threading.Thread(target=self._key_listener, daemon=True)
        self._key_thread.start()

    def _init_ui(self):
        # ... (保持原有的 UI 布局代码不变，为了节省篇幅这里省略，您直接用原来的即可) ...
        # 只需要把 self.btn_calib 加进去
        pass 
    
    # ... (其他方法保持不变) ...

    def _key_listener(self):
        """专业的键盘监听"""
        import keyboard
        import time
        while True:
            if keyboard.is_pressed('F8'):
                self.engine.toggle()
                time.sleep(0.3)
            time.sleep(0.02)