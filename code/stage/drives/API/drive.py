from PyQt5.QtCore import QTimer

from backend.resources.resource import QResource

class QDrive(QResource):
    
    def __init__(self, resource):

        super().__init__(resource)

        # master resource
        self.esp = self.master_int.master

    def move(self, sign):

        # Set disabled state of several interface elements
        self.move_box.abort_pb.setDisabled(False)
        self.move_box.arrow_button_group.setDisabled(True)
        self.move_params.power_cb.setDisabled(True)

        # Construct timer for limit checking and launch it
        self.timer = QTimer()
        self.timer.setInterval(self.config["limits_check_interval"])
        if sign > 0:
            self.timer.timeout.connect(lambda: self.esp.write_message(f"{self.name}_MAX"))
        else:
            self.timer.timeout.connect(lambda: self.esp.write_message(f"{self.name}_MIN"))
        self.timer.start()

        # Calculate params
        nsteps = sign*int(self.move_params.steps_widget.value())
        speed = int(self.move_params.speed_widget.value())
        mstep = int(self.move_params.divider_cb.currentText())

        self.esp.write(f"{self.name}_MST_{mstep}")
        self.esp.write(f"{self.name}_SPD_{speed}")
        self.esp.write(f"{self.name}_MOV_{nsteps}")

        self.is_moving = True

    def on_abort(self):

        self.esp.write(f"{self.name}_MOV_ABT")
        self.on_finish()

    def on_finish(self):

        self.move_box.abort_pb.setDisabled(True)
        self.move_box.arrow_button_group.setDisabled(False)
        self.move_params.power_cb.setDisabled(False)

        self.esp.write(f"{self.name}_MAX")
        self.esp.write(f"{self.name}_MIN")
        self.timer.stop()
        self.is_moving = False
