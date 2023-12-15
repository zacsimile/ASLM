# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only
# (subject to the limitations in the disclaimer below)
# provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Standard Library Imports
import platform
import os

# Third Party Imports

# Local Imports


# Proxy Configuration
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""


def main():
    """Light-sheet Microscopy (Navigate).
    Microscope control software built in a Model-View-Controller architecture.
    Provides control of cameras, data acquisition cards, filter wheels, lasers
    stages, voice coils, and zoom servos.

    Parameters
    ----------
    *args : iterable
        --synthetic_hardware
        --sh
        --config_file
        --experiment_file
        --waveform_constants_path
        --rest_api_file
        --waveform_templates_file
        --logging_config

    Returns
    -------
    None

    Examples
    --------
    >>> python main.py --synthetic_hardware
    """
    import tkinter as tk
    from navigate.controller.controller import Controller
    from navigate.log_files.log_functions import log_setup
    from navigate.view.splash_screen import SplashScreen
    from navigate.tools.main_functions import (
        evaluate_parser_input_arguments,
        create_parser,
    )

    # Start the GUI, withdraw main screen, and show splash screen.
    root = tk.Tk()
    root.withdraw()

    # Splash Screen
    current_directory = os.path.dirname(os.path.realpath(__file__))
    splash_screen = SplashScreen(
        root, os.path.join(current_directory, "view", "icon", "splash_screen_image.png")
    )

    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()

    (
        configuration_path,
        experiment_path,
        waveform_constants_path,
        rest_api_path,
        waveform_templates_path,
        logging_path,
    ) = evaluate_parser_input_arguments(args)

    log_setup("logging.yml", logging_path)

    Controller(
        root,
        splash_screen,
        configuration_path,
        experiment_path,
        waveform_constants_path,
        rest_api_path,
        waveform_templates_path,
        args,
    )
    root.mainloop()


def main_ipython(**kwargs):
    import threading

    class ThreadedAppWrapper(threading.Thread):
        def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
            # import tkinter as tk
            from IPython import get_ipython

            from types import SimpleNamespace

            from navigate.controller.controller import Controller
            from navigate.log_files.log_functions import log_setup
            from navigate.config import get_configuration_paths
            from navigate.view.splash_screen import SplashScreen

            super().__init__(group, target, name, args, kwargs, daemon=True)

            # self.app = tk._default_root
            self.app = get_ipython().kernel.app_wrapper.app

            current_directory = os.path.dirname(os.path.realpath(__file__))
            splash_screen = SplashScreen(
                self.app,
                os.path.join(
                    current_directory, "view", "icon", "splash_screen_image.png"
                ),
            )

            (
                configuration_path,
                experiment_path,
                waveform_constants_path,
                rest_api_path,
                waveform_templates_path,
            ) = get_configuration_paths()
            logging_path = None
            args = SimpleNamespace(**kwargs)

            log_setup("logging.yml", logging_path)

            self.controller = Controller(
                self.app,
                splash_screen,
                configuration_path,
                experiment_path,
                waveform_constants_path,
                rest_api_path,
                waveform_templates_path,
                args,
            )

        def run(self):
            # self.app.mainloop()
            pass

        def get_controller(self):
            return self.controller

    app = ThreadedAppWrapper(kwargs=kwargs)
    app.start()
    return app.get_controller()


if __name__ == "__main__":
    if platform.system() == "Darwin":
        print("Apple OS Not Fully Supported. ")
    main()
