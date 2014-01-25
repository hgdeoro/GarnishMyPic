# -*- coding: utf-8 -*-

#===============================================================================
#
#    Copyright 2013 Horacio Guillermo de Oro <hgdeoro@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import os
import wx

from gmp.garnisher import do_garnish, BORDER_SIZE_BOTTOM
from gmp.utils import GMP_OUTPUT_DIR, GMP_AUTHOR, GMP_FONT,\
    GMP_DEFAULT_FONT_SIZE, GMP_OUTPUT_QUALITY, GMP_BORDER, GMP_COLOR,\
    GMP_DEFAULT_MAX_SIZE, GMP_TITLE, GMP_TITLE_IMAGE, GMP_EXIF_COPYRIGHT


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        """
        When files are dropped, write where they were dropped and then
        the file paths themselves
        """
        self.window.SetInsertionPointEnd()
        self.window.clearText()
        for filepath in filenames:
            self.window.updateText(filepath + '\n')

            self.window.updateText(" + Procesing " + os.path.normpath(os.path.abspath(filepath)) + "...")
            self.window.refreshWindow()
            exit_status = do_garnish(filepath, GMP_OUTPUT_DIR,
                author=GMP_AUTHOR,
                overwrite=True,
                font_file=GMP_FONT,
                font_size=GMP_DEFAULT_FONT_SIZE,
                output_quality=GMP_OUTPUT_QUALITY,
                border_size=GMP_BORDER,
                border_color=GMP_COLOR,
                border_size_bottom=BORDER_SIZE_BOTTOM,
                max_size=[int(x) for x in GMP_DEFAULT_MAX_SIZE.split('x')],
                title=GMP_TITLE,
                title_img=GMP_TITLE_IMAGE,
                year=2014,
                technical_info=True,
                exif_copyright=GMP_EXIF_COPYRIGHT
            )
            self.window.updateText(" OK\n")
            self.window.refreshWindow()

        self.window.updateText("\nFinished!\n")


class DnDPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        file_drop_target = MyFileDropTarget(self)
        lbl = wx.StaticText(self, label="Drag file to process here:")
        self.fileTextCtrl = wx.TextCtrl(self,
                                        style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
        self.fileTextCtrl.SetDropTarget(file_drop_target)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.fileTextCtrl, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def SetInsertionPointEnd(self):
        """
        Put insertion point at end of text control to prevent overwriting
        """
        self.fileTextCtrl.SetInsertionPointEnd()

    def updateText(self, text):
        """
        Write text to the text control
        """
        self.fileTextCtrl.WriteText(text)

    def clearText(self):
        self.fileTextCtrl.Clear()

    def refreshWindow(self):
        self.Refresh()
        self.Update()
        self.UpdateWindowUI()


class DnDFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="DnD for GMP")
        panel = DnDPanel(self)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = DnDFrame()
    app.MainLoop()
