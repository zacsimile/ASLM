# Copyright (c) 2021-2024  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:

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


#  Standard Library Imports
import logging
from typing import Any, Dict

# Third Party Imports

# Local Imports
from navigate.model.devices.remote_focus.base import RemoteFocusBase
from navigate.tools.decorators import log_initialization

# # Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


@log_initialization
class SyntheticRemoteFocus(RemoteFocusBase):
    """SyntheticRemoteFocus Class"""

    def __init__(
        self,
        microscope_name: str,
        device_connection: Any,
        configuration: Dict[str, Any],
    ) -> None:
        """Initialize the SyntheticRemoteFocus class.

        Parameters
        ----------
        microscope_name : str
            The microscope name.
        device_connection : Any
            The device connection object.
        configuration : Dict[str, Any]
            The device configuration.
        """
        super().__init__(microscope_name, device_connection, configuration)
        pass

    @staticmethod
    def move(readout_time, offset=None):
        """Moves the remote focus.

        This method moves the remote focus.

        Parameters
        ----------
        readout_time : float
            The readout time in seconds.
        offset : float
            The offset of the signal in volts.
        """
        logger.debug(f"Remote focus offset and readout time: {offset}, {readout_time}")
