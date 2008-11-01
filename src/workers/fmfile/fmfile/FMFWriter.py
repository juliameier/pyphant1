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

u"""
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

enc=lambda s: unicode(s, "utf-8")

import platform,os
pltform=platform.system()
if pltform=='Linux' or pltform=='Darwin':
    USER=enc(os.environ['LOGNAME'])
elif pltform=='Windows':
    try:
        USER=enc(os.environ['USERNAME'])
    except:
        USER=u"Unidentified User"
else:
    raise NotImplementedError, "Unsupported Platform %s" %pltform

import fmfgen, numpy

def field2fmf(fieldContainer):
    assert len(fieldContainer.data.shape)==1
    dim = fieldContainer.dimensions[0]
    factory = fmfgen.gen_factory(out_coding='utf-8', eol='\n')
    fc = factory.gen_fmf()
    fc.add_reference_item('author', USER)
    data = numpy.vstack([dim.data, fieldContainer.data])
    tab = factory.gen_table(data.transpose())
    tab.add_column_def(dim.longname, dim.shortname, str(dim.unit))
    tab.add_column_def(fieldContainer.longname, 
                       fieldContainer.shortname, 
                       str(fieldContainer.unit),
                       dependencies = [dim.shortname])
    fc.add_table(tab)
    return str(fc)


import wx

class TextFrame(wx.Frame):
    def __init__(self,fmf):
        wx.Frame.__init__(self,None,-1,'FMFWriter', size=(300,200))
        multiText = wx.TextCtrl(self,-1,fmf,size=(200,200),style=wx.TE_MULTILINE)
        multiText.SetInsertionPoint(0)

class FMFWriter(object):
    name='FMF Writer'
    def __init__(self, fieldContainer,show=True):
        self.fieldContainer = fieldContainer
        self.show = show
        self.execute()

    def execute(self):
        self.text =  field2fmf(self.fieldContainer)
        app = wx.PySimpleApp()
        frame = TextFrame(self.text)
        frame.Show()
        app.MainLoop()