"""Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

     * Neither the name of the copyright holders nor the names of its
     contributors may be used to endorse or promote products derived from this
     software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


# Standard Library Imports
import platform
import sys
import logging
import time
import importlib

# Third Party Imports
import serial

# Local Imports
from aslm.tools.common_functions import build_ref_name

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)

class DummyDeviceConnection:
    pass

def auto_redial(func, args, n_tries=10, exception=Exception, **kwargs):
    r"""Retries connections to a startup device defined by func n_tries times.

    Parameters
    ----------
    func : function or class
        The function or class (__init__() function) that connects to a device.
    args : tuple
        Arguments to function or class
    n_tries : int
        The number of tries to redial.
    exception : inherits from BaseException
        An exception type to check on each connection attempt.

    Returns
    -------
    val : object
        Result of func
    """
    val = None

    for i in range(n_tries):
        try:
            val = func(*args, **kwargs)
        except exception:
            if i < (n_tries-1):
                print(f"Failed {str(func)} attempt {i+1}/{n_tries}.")
                # If we failed, but part way through object creation, we must
                # delete the object prior to trying again. This lets us restart
                # the connection process with a clean slate
                if val is not None:
                    val.__del__()
                    del val
                    val = None
                time.sleep(0.5)  # TODO: 0.5 reached by trial and error. Better value?
            else:
                raise exception
        else:
            break

    return val


def load_camera_connection(configuration,
                           camera_id=0,
                           is_synthetic=False):
    r"""Initializes the camera api class.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.
    camera_id : int
        Device ID (0, 1...)
    is_synthetic: bool
        Whether it is a synthetic hardware

    Returns
    -------
    Camera controller: class
        Camera api class.
    """

    if is_synthetic:
        cam_type = 'SyntheticCamera'
    else:
        cam_type = configuration['configuration']['hardware']['camera'][camera_id]['type']

    if cam_type == 'HamamatsuOrca':
        # Locally Import Hamamatsu API and Initialize Camera Controller
        HamamatsuController = importlib.import_module('aslm.model.devices.APIs.hamamatsu.HamamatsuAPI')
        return auto_redial(HamamatsuController.DCAM, (camera_id,), exception=Exception)
    elif cam_type == 'SyntheticCamera':
        from aslm.model.devices.camera.camera_synthetic import SyntheticCameraController
        return SyntheticCameraController()
    else:
        device_not_found('camera', camera_id, cam_type)

def start_camera(microscope_name, device_connection, configuration, is_synthetic=False):
    r"""Initializes the camera class.

    Parameters
    ----------
    microscope name: str
        Microscope name in the configuration yaml file
    camera controller: camera api object
        Camera api object that can communicate with the camera device directly.
    configuration : dict
        Configurator instance of global microscope configuration.
    is_synthetic: bool
        Whether it is a synthetic hardware

    Returns
    -------
    Camera : class
        Camera class.
    """
    if device_connection is None:
        device_not_found(microscope_name, 'camera')
    
    if is_synthetic:
        cam_type = 'SyntheticCamera'
    else:
        cam_type = configuration['configuration']['microscopes'][microscope_name]['camera']['hardware']['type']
    
    if cam_type == 'HamamatsuOrca':
        from aslm.model.devices.camera.camera_hamamatsu import HamamatsuOrca
        return HamamatsuOrca(microscope_name, device_connection, configuration)
    elif cam_type == 'SyntheticCamera':
        from aslm.model.devices.camera.camera_synthetic import SyntheticCamera
        return SyntheticCamera(microscope_name, device_connection, configuration)
    else:
        device_not_found(microscope_name, 'camera', cam_type)


def start_stages(configuration):
    r"""Initializes the stage class on a dedicated thread.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.

    Returns
    -------
    Stage : class
        Stage class.
    """

    stages = configuration['configuration']['hardware']['stage']

    if type(stages) == list:
        for i in range(len(stages)):
            stage_type = configuration['configuration']['hardware']['stage'][i]['type']

            if stage_type == 'PI' and platform.system() == 'Windows':
                from aslm.model.devices.stages.stage_pi import PIStage
                from pipython.pidevice.gcserror import GCSError
                return auto_redial(PIStage, (configuration,), exception=GCSError)
            elif stage_type == 'SyntheticStage':
                from aslm.model.devices.stages.stage_synthetic import SyntheticStage
                return SyntheticStage(configuration)
            else:
                device_not_found(stage_type)
    else:
        stage_type = configuration['configuration']['hardware']['stage']['type']
        if stage_type == 'PI' and platform.system() == 'Windows':
            from aslm.model.devices.stages.stage_pi import PIStage
            from pipython.pidevice.gcserror import GCSError
            return auto_redial(PIStage, (configuration,), exception=GCSError)
        elif stage_type == 'SyntheticStage':
            from aslm.model.devices.stages.stage_synthetic import SyntheticStage
            return SyntheticStage(configuration)
        else:
            device_not_found(stage_type)

def start_stages_r(configuration):
    r"""Initializes a focusing stage class in a dedicated thread.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.

    Returns
    -------
    Stage : class
        Stage class.
    """
    if configuration['configuration']['hardware']['stage'][1]['type'] == 'Thorlabs' and platform.system() == 'Windows':
        from aslm.model.devices.stages.stage_tl_kcube_inertial import TLKIMStage
        from aslm.model.devices.APIs.thorlabs.kcube_inertial import TLFTDICommunicationError
        return auto_redial(TLKIMStage, (configuration,), exception=TLFTDICommunicationError)
    else:
        device_not_found(configuration['configuration']['hardware']['stage'][1]['type'])


def load_zoom_connection(configuration, is_synthetic=False):
    device_info = configuration['configuration']['hardware']['zoom']
    if is_synthetic:
        device_type = 'SyntheticZoom'
    else:
        device_type = device_info['type']
    
    if device_type == 'DynamixelZoom':
        from aslm.model.devices.zoom.zoom_dynamixel import build_dynamixel_zoom_connection
        return auto_redial(build_dynamixel_zoom_connection, (configuration,), exception=Exception)
    elif device_type == 'SyntheticZoom':
        return DummyDeviceConnection()
    else:
        device_not_found('Zoom', device_type)

def start_zoom(microscope_name, device_connection, configuration, is_synthetic=False):
    r"""Initializes the zoom class on a dedicated thread.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.

    Returns
    -------
    Zoom : class
        Zoom class.
    """
    if is_synthetic:
        device_type = 'SyntheticZoom'
    elif 'hardware' in configuration['configuration']['microscopes'][microscope_name]['zoom']:
        device_type = configuration['configuration']['microscopes'][microscope_name]['zoom']['hardware']['type']
    else:
        device_type = 'NoDevice'

    if device_type == 'DynamixelZoom':
        from aslm.model.devices.zoom.zoom_dynamixel import DynamixelZoom
        return DynamixelZoom(microscope_name, device_connection, configuration)
    elif device_type == 'SyntheticZoom':
        from aslm.model.devices.zoom.zoom_synthetic import SyntheticZoom
        return SyntheticZoom(microscope_name, device_connection, configuration)
    elif device_type == 'NoDevice':
        from aslm.model.devices.zoom.zoom_base import ZoomBase
        return ZoomBase(microscope_name, device_connection, configuration)
    else:
        device_not_found(configuration['configuration']['hardware']['zoom']['type'])

def load_filter_wheel_connection(configuration, is_synthetic=False):
    device_info = configuration['configuration']['hardware']['filter_wheel']
    if is_synthetic:
        device_type = 'SyntheticFilterWheel'
    else:
        device_type = device_info['type']
    
    if device_type == 'SutterFilterWheel':
        return auto_redial(serial.Serial, (device_info['comport'], device_info['baudrate'],), timeout=.25, exception=Exception)
    elif device_type == 'SyntheticFilterWheel':
        return DummyDeviceConnection()
    else:
        device_not_found('filter_wheel', device_type)

def start_filter_wheel(microscope_name, device_connection, configuration, is_synthetic=False):
    r"""Initializes the filter wheel class on a dedicated thread.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.

    Returns
    -------
    FilterWheel : class
        FilterWheel class.
    """
    if device_connection is None:
        device_not_found(microscope_name, 'filter_wheel')

    if is_synthetic:
        device_type = 'SyntheticFilterWheel'
    else:
        device_type = configuration['configuration']['microscopes'][microscope_name]['filter_wheel']['hardware']['type']

    if device_type == 'SutterFilterWheel':        
        from aslm.model.devices.filter_wheel.filter_wheel_sutter import SutterFilterWheel
        return SutterFilterWheel(microscope_name, device_connection, configuration)
    elif device_type == 'SyntheticFilterWheel':
        from aslm.model.devices.filter_wheel.filter_wheel_synthetic import SyntheticFilterWheel
        return SyntheticFilterWheel(microscope_name, device_connection, configuration)
    else:
        device_not_found(microscope_name, 'filter_wheel', device_type)


def start_daq(configuration, is_synthetic=False):
    r"""Initializes the data acquisition (DAQ) class on a dedicated thread.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.

    Returns
    -------
    DAQ : class
        DAQ class.
    """
    if is_synthetic:
        device_type = 'SyntheticDAQ'
    else:
        device_type = configuration['configuration']['hardware']['daq']['type']

    if device_type == 'NI':
        from aslm.model.devices.daq.daq_ni import NIDAQ
        return NIDAQ(configuration)
    elif device_type == 'SyntheticDAQ':
        from aslm.model.devices.daq.daq_synthetic import SyntheticDAQ
        return SyntheticDAQ(configuration)
    else:
        device_not_found(configuration['configuration']['hardware']['daq']['type'])


def start_shutter(microscope_name, device_connection, configuration, is_synthetic=False):
    r"""Initializes the shutter class on a dedicated thread.

    Initializes the shutters: ThorlabsShutter or SyntheticShutter
    Shutters are triggered via digital outputs on the NI DAQ Card
    Thus, requires both to be enabled.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.

    Returns
    -------
    Shutter : class
        Shutter class.
    """

    if is_synthetic:
        device_type = 'SyntheticShutter'
    else:
        device_type = configuration['configuration']['microscopes'][microscope_name]['shutter']['hardware']['type']

    if device_type == 'NI':
        if device_connection is not None:
            return device_connection
        from aslm.model.devices.shutter.laser_shutter_ttl import ShutterTTL
        return ShutterTTL(microscope_name, None, configuration)
    elif device_type == 'SyntheticShutter':
        if device_connection is not None:
            return device_connection
        from aslm.model.devices.shutter.laser_shutter_synthetic import SyntheticShutter
        return SyntheticShutter(microscope_name, None, configuration)
    else:
        device_not_found(microscope_name, 'shutter', device_type)


def start_lasers(microscope_name, device_connection, configuration, id=0, is_synthetic=False):
    r"""Initializes the laser trigger class on a dedicated thread.

    Initializes the Laser Switching, Analog, and Digital DAQ Outputs.

    Parameters
    ----------
    configuration : dict
        Configurator instance of global microscope configuration.
    experiment : dict
        Configurator instance of experiment configuration.

    Returns
    -------
    Triggers : class
        Trigger class.
    """

    if is_synthetic:
        device_type = 'SyntheticLaser'
    else:
        device_type = configuration['configuration']['microscopes'][microscope_name]['lasers'][id]['onoff']['hardware']['type']

    if device_type == 'NI':
        if device_connection is not None:
            return device_connection
        from aslm.model.devices.lasers.laser_ni import LaserNI
        return LaserNI(microscope_name, device_connection, configuration, id)
    elif device_type == 'SyntheticLaser':
        if device_connection is not None:
            return device_connection
        from aslm.model.devices.lasers.laser_synthetic import SyntheticLaser
        return SyntheticLaser(microscope_name, device_connection, configuration, id)
    else:
        device_not_found(microscope_name, 'laser', device_type, id)

def start_remote_focus_device(microscope_name, device_connection, configuration, is_synthetic=False):
    if is_synthetic:
        device_type = 'SyntheticRemoteFocus'
    else:
        device_type = configuration['configuration']['microscopes'][microscope_name]['remote_focus_device']['hardware']['type']
    
    if device_type == 'NI':
        from aslm.model.devices.remote_focus.remote_focus_ni import RemoteFocusNI
        return RemoteFocusNI(microscope_name, device_connection, configuration)
    elif device_type == 'SyntheticRemoteFocus':
        from aslm.model.devices.remote_focus.remote_focus_synthetic import SyntheticRemoteFocus
        return SyntheticRemoteFocus(microscope_name, device_connection, configuration)
    else:
        device_not_found(microscope_name, 'remote_focus', device_type)

def start_galvo(microscope_name, device_connection, configuration, id=0, is_synthetic=False):
    if is_synthetic:
        device_type = 'SyntheticGalvo'
    else:
        device_type = configuration['configuration']['microscopes'][microscope_name]['galvo'][id]['hardware']['type']

    if device_type == 'NI':
        from aslm.model.devices.galvo.galvo_ni import GalvoNI
        return GalvoNI(microscope_name, device_connection, configuration, id)
    elif device_type == 'SyntheticGalvo':
        from aslm.model.devices.galvo.galvo_synthetic import SyntheticGalvo
        return SyntheticGalvo(microscope_name, device_connection, configuration, id)
    else:
        device_not_found(microscope_name, 'galvo', id, device_type)

def device_not_found(*args):

    print("Device Not Found in Configuration.YML:", args)
    sys.exit()

def load_devices(configuration, is_synthetic=False)->dict:
    devices = {}
    # load camera
    if 'camera' in configuration['configuration']['hardware'].keys():
        devices['camera'] = {}
        for id, device in enumerate(configuration['configuration']['hardware']['camera']):
            device_ref_name = build_ref_name('_', device['type'], device['serial_number'])
            devices['camera'][device_ref_name] = load_camera_connection(configuration, id, is_synthetic)
            
    # load filter wheel
    if 'filter_wheel' in configuration['configuration']['hardware'].keys():
        devices['filter_wheel'] = {}
        device = configuration['configuration']['hardware']['filter_wheel']
        devices['filter_wheel'][device['type']] = load_filter_wheel_connection(configuration, is_synthetic)

    # load zoom
    if 'zoom' in configuration['configuration']['hardware'].keys():
        devices['zoom'] = {}
        device = configuration['configuration']['hardware']['zoom']
        device_ref_name = build_ref_name('_', device['type'], device['servo_id'])
        devices['zoom'][device_ref_name] = load_zoom_connection(configuration, is_synthetic)

    # load daq
    if 'daq' in configuration['configuration']['hardware'].keys():
        devices['daq'] = start_daq(configuration, is_synthetic)

    return devices