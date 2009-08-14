# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import (Worker, Connectors, Param)
from pyphant.core.KnowledgeManager import KnowledgeManager as KM
from pyphant.core import PyTablesPersister
from copy import deepcopy
from pyphant.core.DataContainer import FieldContainer
import numpy
from tools import Emd5Src

PARAMBY = [u"don't map",
           u"source/dest",
           u"columns of input SC"]

def batch(inputSC, recipe, plug,
          paramMethod, paramSource, paramDestWorker, paramDest, paramConvert):
    socket = recipe.getOpenSocketsForPlug(plug)[0]
    input_emd5s = inputSC['emd5'].data
    km = KM.getInstance()
    output_emd5s = []
    emd5src = Emd5Src.Emd5Src()
    emd5src.paramSelectby.value = u"enter emd5"
    if paramMethod == PARAMBY[1]:
            paramFC = inputSC[paramSource]
    rowcount = 0
    for input_emd5 in input_emd5s:
        input_dc = km.getDataContainer(input_emd5)
        if socket._plug != None:
            socket.pullPlug()
        emd5src.paramEnteremd5.value = unicode(input_emd5)
        if paramMethod == PARAMBY[1]:
            fc = inputSC[paramSource]
            paramval = paramFC.data[rowcount]
            try:
                withUnit = paramval * paramFC.unit
                paramval = withUnit
            except:
                pass
            if paramConvert:
                paramval = paramval.__str__()
            paramDestWorker.getParam(paramDest).value = paramval
        socket.insert(emd5src.getPlugs()[0])
        output_dc = plug.getResult()
        output_dc.seal()
        km.registerDataContainer(output_dc)
        output_emd5s.append(output_dc.id)
        rowcount += 1
    outputSC = deepcopy(inputSC)
    output_columns = []
    for col in outputSC.columns:
        if col.longname == 'emd5':
            output_columns.append(FieldContainer(numpy.array(output_emd5s),
                                                 longname='emd5'))
        else:
            output_columns.append(col)
    outputSC.columns = output_columns
    outputSC.seal()
    return outputSC


class BatchWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "Batch"
    _params = [("worker", "Output worker (input via single open socket)",
                [u"None"], None),
               ("plug", "Output plug (OK to update)", [u"None"], None),
               ("paramBy", "Map parameters via", PARAMBY, None),
               ("paramSource", "Parameter source", [u"None"], None),
               ("paramDestWorker", "Parameter destination worker",
                [u"None"], None),
               ("paramDest",
                "Parameter destination (OK to update)", [u"None"], None),
               ("paramConvert", "Convert parameter to string", False, None)]
    _sockets = [("emd5SC", Connectors.TYPE_ARRAY)]

    def refreshParams(self, subscriber = None):
        wlist = self.parent.getWorkers()
        self.paramWorker.possibleValues = [unicode(
                worker.getParam('name').value) for worker in wlist]
        self.paramParamDestWorker.possibleValues = [unicode(
                worker.getParam('name').value) for worker in wlist]
        try:
            worker = self.parent.getWorker(
                self.paramWorker.value.encode('utf-8'))
            plist = worker.getPlugs()
        except:
            plist = self.parent.getAllPlugs()
        self.paramPlug.possibleValues = [unicode(plug.name) for plug in plist]
        if self.socketEmd5SC.isFull():
            tempSC = self.socketEmd5SC.getResult(subscriber)
            self.paramParamSource.possibleValues = [unicode(
                    key) for key in tempSC.longnames.keys()]
        try:
            pardest = self.parent.getWorker(
                self.paramParamDestWorker.value.encode('utf-8')).getParamList()
            destlist = [unicode(param.name) for param in pardest]
        except:
            destlist = [u"None"]
        self.paramParamDest.possibleValues = destlist

    @Worker.plug(Connectors.TYPE_ARRAY)
    def execute(self, emd5SC, subscriber = 0):
        recipe = self.parent
        worker = recipe.getWorker(self.paramWorker.value.encode('utf-8'))
        plug = worker._plugs[self.paramPlug.value.encode('utf-8')]
        paramMethod = self.paramParamBy.value
        if paramMethod != PARAMBY[0]:
            paramDestWorker = recipe.getWorker(
                self.paramParamDestWorker.value.encode('utf-8'))
        else:
            paramDestWorker = None
        if paramMethod == PARAMBY[1]:
            paramSource = unicode(self.paramParamSource.value).encode('utf-8')
            paramDest = unicode(self.paramParamDest.value).encode('utf-8')
        else:
            paramSource = None
            paramDest = None
        paramConvert = self.paramParamConvert.value
        return batch(emd5SC, recipe, plug,
                     paramMethod, paramSource,
                     paramDestWorker, paramDest, paramConvert)
