from wxPython.wx import *
from config import *
import PHPUnserialize
import fcntl # for flock
import random


class SodaIdleStatsPanel(wxPanel):
    def __init__(self, parent, ID, pos, size):
        wxPanel.__init__(self, parent, ID, pos, size)

class BarGraphPanel(SodaIdleStatsPanel):
    def __init__(self, parent, ID, pos, size, stats_list, min, max, title=None):
        SodaIdleStatsPanel.__init__(self, parent, ID, pos, size)

        font = self.GetFont()
        font.SetPointSize(SodaStatsFontSize)

        self.statsSizer = wxBoxSizer(wxVERTICAL)
        self.SetSizer(self.statsSizer)
        self.SetBackgroundColour(parent.GetBackgroundColour())

        barpad = 20 * len(str(min)) 
        padding = 10
        # Column width
        cw = size.GetWidth() - padding * 2

        if title is not None:
            sizer = wxBoxSizer(wxHORIZONTAL)
            titletxt = wxStaticText(self,   
                                       -1, 
                                       title,
                                       wxDefaultPosition,
                                       wxSize(cw, -1),
                                       style=wxALIGN_CENTRE)
            titletxt.SetFont(font)
            titletxt.SetForegroundColour("#ffffff")
            sizer.Add(titletxt)
            self.statsSizer.Add(sizer)

        for val in stats_list:
            sizer = wxBoxSizer(wxHORIZONTAL)

            w = (cw - barpad) * 0.75 * (val[0] - min) / max + barpad

            label = wxStaticText(self,
                                       -1,
                                       val[1],
                                       wxDefaultPosition,
                                       wxSize(cw * 0.25, -1))

            label.SetForegroundColour(SodaOrange)
            label.SetFont(font)

            numberSizer = wxBoxSizer(wxVERTICAL)

            numberPanel = wxPanel(self, -1)
            number = wxStaticText(numberPanel,
                                       -1,
                                       str(val[0]),
                                       wxDefaultPosition,
                                       wxSize(w, SodaStatsFontSize*1.5),
                                       style=wxALIGN_RIGHT)
            # This spacing/padding comes out different on different
            # machines.
            number.SetFont(font)

            numberPanel.SetBackgroundColour(SodaLightGreen)
            numberPanel.SetSizer(numberSizer)

            numberSizer.Add(number, proportion=0)

            sizer.AddSpacer(wxSize(padding, -1))
            sizer.Add(label)
            sizer.Add(numberPanel)

            self.statsSizer.Add(sizer)
            self.statsSizer.AddSpacer(wxSize(1, 1))

# This could probably be generalized a little better
class SodaIdleSodaStatsPanel(BarGraphPanel):
    sodaStatsPath = "/var/soda/stockcount.psr"
    unserializer = PHPUnserialize.PHPUnserialize()

    def __init__(self, parent, ID, pos, size):
        file = open(self.sodaStatsPath, "r")
        fcntl.flock(file, fcntl.LOCK_SH);
        stats = self.unserializer.unserialize(file.read())
        fcntl.flock(file, fcntl.LOCK_UN);
        file.close()

        stats_keys = filter(lambda x: x != "r10", stats.keys())
        stats_list = [(stats[key]["sold"], stats[key]["name"]) for key in stats_keys]
        stats_list.sort(cmp=lambda x,y:cmp(y,x))

        min = stats_list[-1][0]
        max = stats_list[0][0]

        BarGraphPanel.__init__(self, parent, ID, pos, size, stats_list, min, max)

class SodaIdleWallOfShamePanel(SodaIdleStatsPanel):
    def __init__(self, parent, ID, pos, size):
        SodaIdleStatsPanel.__init__(self, parent, ID, pos, size)
        self.parent = parent

        font = self.GetFont()
        font.SetPointSize(SodaStatsFontSize)

        columns = 3

        self.sizer = wxBoxSizer(wxVERTICAL)

        self.statsSizers = []
        for c in range(columns):
          self.statsSizers.append(wxBoxSizer(wxVERTICAL))

        self.columnSizer = wxBoxSizer(wxHORIZONTAL)

        self.SetSizer(self.sizer)
        self.SetBackgroundColour(parent.GetBackgroundColour())

        entries_per_column = 8
        padding = 10
        # Column width
        cw = size.GetWidth() - padding * 4

        title = wxStaticText(self,
                                   -1,
                                   "Wall of Shame",
                                   wxDefaultPosition,
                                   wxSize(cw,-1),
                                   style=wxALIGN_CENTRE)

        title_font = self.GetFont()
        title_font.SetPointSize(SodaLargeSize)
        title.SetForegroundColour(SodaWhite)
        title.SetFont(title_font)

        self.sizer.Add(title)



        def add_to_sizer(s, e):
            sizer = wxBoxSizer(wxHORIZONTAL)

            label = wxStaticText(self,
                                       -1,
                                       e['username'],

                                       wxDefaultPosition,
                                       wxSize(cw * 0.35, -1))

            label.SetForegroundColour(SodaOrange)
            label.SetFont(font)

            #number = wxStaticText(self,
            #                           -1,
            #                           str('-$%0.2f' % (-e['balance'],)),
            #                           wxDefaultPosition,
            #                           wxSize(cw * 0.15, -1),
            #                           style=wxALIGN_RIGHT)

            #number.SetForegroundColour(SodaOrange)
            #number.SetFont(font)

            sizer.Add(label)
            #sizer.Add(number)

            s.Add(sizer)

        self.wall_of_shame = self.parent.parent.getWallOfShame()
        total_entries = columns * entries_per_column

        if total_entries < len(self.wall_of_shame):
          self.wall_of_shame = random.sample(self.wall_of_shame, total_entries)

        for i,e in enumerate(self.wall_of_shame):
          add_to_sizer(self.statsSizers[int(i/entries_per_column)], e)

        for sizer in self.statsSizers:
            self.columnSizer.AddSpacer(wxSize(padding, -1))
            self.columnSizer.Add(sizer)
        self.columnSizer.AddSpacer(wxSize(padding, -1))
        self.sizer.Add(self.columnSizer)
