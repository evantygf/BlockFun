# Copyright 2016 Evan Dunning
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#Data is an id that has metadata (such as what items are in a chest)
class Data:
    def __init__(self, id, metadata=None):
        self.id = id
        self.metadata = metadata
        if self.id == 9 and self.metadata == None:
            self.metadata = [None for i in range(5)]