# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
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

#  Standard Imports

# Third Party Imports
# import zarr
import numpy.typing as npt

# Local imports
from .data_source import DataSource


class ZarrDataSource(DataSource):
    def __init__(self, file_name: str = "", mode: str = "w") -> None:
        self.image = None
        self.__store = None
        super().__init__(file_name, mode)

    def write(self, data: npt.ArrayLike, **kw) -> None:
        self.mode = "w"

        c, z, t, p = self._cztp_indices(
            self._current_frame, self.metadata.per_stack
        )  # find current channel
        if (z == 0) and (c == 0) and (t == 0) and (p == 0):
            self._setup_zarr()

        self._current_frame += 1

        # Check if this was the last frame to write
        c, z, t, p = self._cztp_indices(self._current_frame, self.metadata.per_stack)
        if (z == 0) and (c == 0) and ((t >= self.shape_t) or (p >= self.positions)):
            self.close()

    def _setup_zarr(self):
        if self.positions > 0:
            # https://ngff.openmicroscopy.org/latest/#hcs-layout
            pass
        else:
            # https://ngff.openmicroscopy.org/latest/#image-layout
            pass
        pass

    def _mode_checks(self) -> None:
        self._write_mode = self._mode == "w"
        self.close()  # if anything was already open, close it
        if self._write_mode:
            self._current_frame = 0
            self._views = []
            self._setup_zarr()
        else:
            self.read()
        self._closed = False

    def close(self) -> None:
        if self._closed:
            return
        self._check_shape(self._current_frame - 1, self.metadata.per_stack)
        self.__store.close()
        self._closed = True
