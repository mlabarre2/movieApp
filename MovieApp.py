import wx
import requests
import webbrowser
import locale

class MovieApp(wx.Frame):
    def __init__(self, *args, **keywords):
        wx.Frame.__init__(self, *args, **keywords)
        
        self.img_blank = wx.Bitmap(name='/Users/matthewlabarre/Documents/School/Penn/Junior/logos/blank.png')
        self.imdb = wx.Bitmap(name='/Users/matthewlabarre/Documents/School/Penn/Junior/logos/imdb.png')
        self.metacritic = wx.Bitmap(name='/Users/matthewlabarre/Documents/School/Penn/Junior/logos/metacritic.png')
        self.rotten = wx.Bitmap(name='/Users/matthewlabarre/Documents/School/Penn/Junior/logos/rottentomatoes.jpeg')
        
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.SetSizer(sizer)
        
        self.text_box = wx.TextCtrl(self)
        self.text_box.Bind(wx.EVT_KEY_DOWN, self.onEnter)
        
        self.CreateTextCtrl()
        self.CreateMainArea()
        self.More()
        
        
        
        sizer.Fit(self)
        
        self.get_movies = ""
        
        self.movie_info_dict = {}
        
        self.showData = False

    def CreateTextCtrl(self):
        self.GetSizer().Add(item=self.text_box,flag=wx.EXPAND | wx.ALIGN_CENTER)
        
        
    def onEnter(self, event):
        self.mainposition = self.GetPosition()
        self.mainsize = self.GetSize()
        self.showData = True
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER: 
            temp = self.text_box.GetValue()
            if "," in temp:
                self.person = temp[0 : temp.index(",")]
                self.role = temp[temp.index(",") + 2:]
                self.person_list = personsearch(self.person, self.role, self.texts, self.movie_info_dict,
                                                parent = None, id = wx.ID_ANY, title = "Person Search",
                                                pos = (self.mainposition[0] + self.mainsize[0], self.mainposition[1]))
                self.person_list.Show()
            else:
                self.movie_name = temp
            
                self.get_movies = requests.get("http://api.themoviedb.org/3/search/movie?" \
                                          + "api_key=53ccaeeec873e469b9095c922f50356c&" \
                                          + "query=" + self.movie_name.replace(" ", "+"))
                
                if self.get_movies.json().get('total_results') == 0:
                    wx.MessageBox('No movies found!', 'Error', wx.OK)
                elif self.get_movies.json().get('total_results') > 1:
                    self.new = window2(self.get_movies, self.texts, self.text_box, \
                                       self.movie_info_dict, parent=None, id=wx.ID_ANY, title='Movie List',
                                       pos = (self.mainposition[0] + self.mainsize[0], self.mainposition[1]))

                    self.new.Show()
                else :
                    self.movie_info_dict['tmdb_id'] = self.get_movies.json().get('results')[0].get('id')
                    
                    get_imdb_rec = requests.get("http://api.themoviedb.org/3/movie/" \
                                        + str(self.movie_info_dict['tmdb_id']) + \
                                        "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338")
                    
                    self.movie_info_dict['imdb_id'] = get_imdb_rec.json().get('imdb_id')
                    get_imdb_rating = requests.get("http://www.omdbapi.com/?i=" + self.movie_info_dict['imdb_id'])
                    self.movie_info_dict['imdb_rating'] = get_imdb_rating.json().get('imdbRating')
                    self.texts[0][1].SetLabel(self.movie_info_dict['imdb_rating'])
                    
                    
                    self.get_rt_rec = requests.get("http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?id=" \
                                              + self.movie_info_dict['imdb_id'][2:] + 
                                              "&type=imdb&apikey=zst8y6gxzjsckez2tautu6xk");
                    try:
                        self.movie_info_dict['rt_critics'] = str(self.get_rt_rec.json().get('ratings').get('critics_score'))
                        self.movie_info_dict['rt_audience'] = str(self.get_rt_rec.json().get('ratings').get('audience_score'))
                        rt_label = "Critics: " + self.movie_info_dict['rt_critics'] + "%" + "\n" + "Audience: " + \
                        self.movie_info_dict['rt_audience'] + "%"
                        self.texts[1][1].SetLabel(rt_label)
                    except AttributeError:
                        wx.MessageBox('No Rotten Tomatoes data found!', 'Error', wx.OK)
                        self.texts[1][1].SetLabel("")
                    self.movie_info_dict['meta_rating'] = get_imdb_rating.json().get("Metascore")
                    self.texts[2][1].SetLabel(self.movie_info_dict['meta_rating'])
                    
                    self.text_box.SetValue(get_imdb_rating.json().get("Title"))
        else:
            event.Skip()
        
    def CreateMainArea(self):
        gs = wx.GridSizer(3, 2)
                
        self.buttons = [[None for i in range(0, 2)] for j in range(0, 3)]
        self.texts = [[None for k in range(0, 2)] for l in range(0, 3)]
        
        for i in range(0,3):
            for j in range (0,2):
                if j == 1:
                    s = wx.StaticText(parent = self, id = i, style=wx.ALIGN_CENTER_VERTICAL)
                    gs.Add(item = s)
                    self.texts[i][j] = s
                    font1 = wx.Font(25, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Calibri')
                    s.SetFont(font1)
                    s.Bind(event=wx.EVT_KEY_DOWN, handler=self.onEnter)
                else: 
                    b = wx.BitmapButton(parent=self, id=wx.ID_ANY, bitmap=self.img_blank)
                    self.buttons[i][j] = b
                    gs.Add(item = b)
                    self.Bind(event=wx.EVT_BUTTON, handler=self.Click, source=b)
                
        self.buttons[0][0].SetBitmapLabel(bitmap = self.imdb)
        self.buttons[2][0].SetBitmapLabel(bitmap = self.metacritic)
        self.buttons[1][0].SetBitmapLabel(bitmap = self.rotten)
        
        
        self.GetSizer().Add(item=gs)
    
    def Click(self, event):
        b = event.GetEventObject()
        label = b.GetBitmapLabel()
        
        if label == self.imdb:
            webbrowser.get('safari').open("www.imdb.com/title/" + str(self.movie_info_dict['imdb_id']))
        elif label == self.metacritic:
            webbrowser.get('safari').open("www.metacritic.com/movie/" + \
                                          self.text_box.GetValue().lower().replace(" ", "-"))
        elif label == self.rotten:
            rt = requests.get("http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?id=" \
                                          + self.movie_info_dict['imdb_id'][2:] + 
                                          "&type=imdb&apikey=zst8y6gxzjsckez2tautu6xk")
            try:
                link = rt.json().get("links").get("alternate")
                webbrowser.get('safari').open(link)
            except AttributeError:
                wx.MessageBox('No Rotten Tomatoes website found!', 'Error', wx.OK)

                
            
    def More(self):
        b = wx.Button(parent = self, id = wx.ID_ANY, label = "More Info")
        self.Bind(wx.EVT_BUTTON, handler = self.MoreClick, source = b)
        self.GetSizer().Add(item=b, flag=wx.EXPAND)
        
    def MoreClick(self, event):
        b = event.GetEventObject()

        self.new2 = window3(self.movie_info_dict['imdb_id'],parent=None, id=wx.ID_ANY, title='More Information',
                                   pos = (self.GetPosition()[0] + self.GetSize()[0], self.GetPosition()[1]))
        
        self.new2.Show()
        
    
class window3(wx.Frame):
    def __init__(self, imdb_id, *args, **keywords):
        locale.setlocale(locale.LC_ALL, 'en_US')
        
        wx.Frame.__init__(self, *args, **keywords)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        
        self.imdb_id = imdb_id
        
        s = wx.StaticText(parent = self, id = wx.ID_ANY, style=wx.ALIGN_CENTER_VERTICAL)
        vsizer.Add(item = s)
        
        self.tmdb_info_getter = requests.get("http://api.themoviedb.org/3/movie/" + \
                                              self.imdb_id + \
                                              "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338")
        self.tmdb_id = str(self.tmdb_info_getter.json().get('id'))
        
        self.title = self.tmdb_info_getter.json().get('title')
        self.runtime = str(self.tmdb_info_getter.json().get('runtime')) + " minutes"
        self.overview = self.tmdb_info_getter.json().get('overview')
        self.budget = locale.format("%d", self.tmdb_info_getter.json().get('budget'), grouping=True)
        self.revenue = locale.format("%d", self.tmdb_info_getter.json().get('revenue'), grouping=True)
        
        genre_list = []
        for i in self.tmdb_info_getter.json().get('genres'):
            genre_list.append(i.get('name'))
        
        self.genres = ", ".join(genre_list)
        self.imdb_info_getter = requests.get("http://www.omdbapi.com/?i=" + self.imdb_id)
        self.director = self.imdb_info_getter.json().get('Director')
        self.actors = self.imdb_info_getter.json().get('Actors')
        self.released = self.imdb_info_getter.json().get('Released')
        
        
        self.text = ("Title: " + self.title + "\n\n" + 
                    "Overview: " + self.overview + "\n\n" + 
                    "Runtime: " + self.runtime + "\n\n" +
                    "Genre: " + self.genres + "\n\n" +  
                    "Director: " + self.director + "\n\n" +
                    "Actors: " + self.actors + "\n\n" +
                    "Budget: $" + self.budget + "\n" +
                    "Box Office Revenue: $" + self.revenue)
        
        s.SetLabel(self.text)
        s.Wrap(500)
        vsizer.Fit(self)
        
                

class window2(wx.Frame):
    def __init__(self, get_movies, buttons, text, movie_info_dict, *args, **keywords):
        wx.Frame.__init__(self, *args, **keywords)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.temp = buttons
        self.text = text
        director = ""
        self.movie_info_dic = movie_info_dict
        
        
        self.movie_dict = {}
        
        self.top_movies = sorted(get_movies.json().get("results"), 
                            key=lambda k: k['popularity'], reverse=True)
        
        for i in range(0,min(len(self.top_movies), 10)):
            movie_name = self.top_movies[i].get('title')
    
            director_req = requests.get("http://api.themoviedb.org/3/movie/" + \
                                        str(self.top_movies[i].get('id')) + \
                                        "/credits?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338")
            for dic in director_req.json().get("crew"):
                for k in dic:
                    if dic.get(k) == "Directing":
                        director = dic.get("name")
            
            year = self.top_movies[i].get("release_date")[0:4]
            label = "Movie: " + movie_name + "\n" + "Director: " + director + "\n" + "Year: " + year
            button = wx.Button(self, -1, label)
            button.myname = movie_name + year
            button.Bind(wx.EVT_BUTTON, self.onButton)
            vsizer.Add(button, 1, wx.EXPAND)
            self.movie_dict[movie_name + year] = self.top_movies[i].get('id')
            
        hsizer1.Add(vsizer,.1,wx.EXPAND)
        self.SetSizer(hsizer1)
        hsizer1.Fit(self)


    def onButton(self,event):
        name = event.GetEventObject().myname

        get_imdb_rec = requests.get("http://api.themoviedb.org/3/movie/" \
                                    + str(self.movie_dict.get(name)) + \
                                    "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338")
        
        imdb_id = get_imdb_rec.json().get('imdb_id')
        self.movie_info_dic['imdb_id'] = imdb_id
        get_imdb_rating = requests.get("http://www.omdbapi.com/?i=" + imdb_id)
        imdb_rating = get_imdb_rating.json().get('imdbRating')
        self.temp[0][1].SetLabel(imdb_rating)
        
        
        get_rt_rec = requests.get("http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?id=" \
                                  + imdb_id[2:] + 
                                  "&type=imdb&apikey=zst8y6gxzjsckez2tautu6xk");
        try:
            rt_critics = str(get_rt_rec.json().get('ratings').get('critics_score'))
            rt_audience = str(get_rt_rec.json().get('ratings').get('audience_score'))
            rt_label = "Critics: " + rt_critics + "%" + "\n" + "Audience: " + rt_audience + "%"
            self.temp[1][1].SetLabel(rt_label)
        except AttributeError:
            wx.MessageBox('No Rotten Tomatoes data found!', 'Error', wx.OK)
            self.temp[1][1].SetLabel("")
        meta_rating = get_imdb_rating.json().get("Metascore")
        self.temp[2][1].SetLabel(meta_rating)
        
        self.text.SetValue(get_imdb_rating.json().get("Title"))
        self.Destroy()
        
        

class personsearch(wx.Frame):
    def __init__(self, person, role, buttons, movie_info_dict, *args, **keywords):
        wx.Frame.__init__(self, *args, **keywords)
        self.movie_info_dict = movie_info_dict
        self.buttons = buttons
        self.person = person
        self.role = role
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        
        
        
        persondict = requests.get("http://api.themoviedb.org/3/search/" +
            "person?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338&query=" +
            self.person.replace(" ", "+")).json()
        if persondict.get("total_results") == 0:
            wx.MessageBox('Person not found! Please check spelling', 'Error', wx.OK)
        
        for i in persondict.get("results"):
            tempHSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            label = i.get("name")
            id1 = i.get("id")
            button = wx.Button(self, -1, label)
            button.myname = (id1, label)
            button.Bind(wx.EVT_BUTTON, self.onButton)
            tempHSizer.Add(button)
            
            label2 = "IMDB Link"
            id2 = requests.get("http://api.themoviedb.org/3/person/" + 
                               str(id1) + "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338").json().get('imdb_id')
            button2 = wx.Button(self, -1, label2)
            button2.myname = id2
            button2.Bind(wx.EVT_BUTTON, self.onButton2)
            tempHSizer.Add(button2)
            
            vsizer.Add(tempHSizer, 1, wx.EXPAND)
        
        hsizer1.Add(vsizer,.1,wx.EXPAND)
        self.SetSizer(hsizer1)
        hsizer1.Fit(self)
    
    def onButton(self,event):
        self.id = event.GetEventObject().myname
        movie_list = window4(self.id[0], self.role, self.buttons, self.movie_info_dict, 
                             parent=None, id=wx.ID_ANY, title=self.id[1] + " Movies",
                             pos = (600, 50))
        movie_list.Show()
        self.Destroy()
        
    def onButton2(self, event):
        self.link = "http://www.imdb.com/name/" + event.GetEventObject().myname
        webbrowser.get('safari').open(self.link)
        
         

class window4(wx.Frame):
    def __init__(self, tmdb, role, buttons, movie_info_dict, *args, **keywords):
        wx.Frame.__init__(self, *args, **keywords)
        
        self.movie_info_dict = movie_info_dict
        self.tmdb = tmdb
        self.role = role
        self.buttons = buttons
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        
        
        self.credits = requests.get("http://api.themoviedb.org/3/person/" + 
                                    str(self.tmdb) + "/movie_credits?" + 
                                    "api_key=53ccaeeec873e469b9095c922f50356c&tt0120338")
        self.imdbdict = {}
        self.dirdict = {}
        self.actdict = {}
        self.imdbdict2 = {}
        
        if self.role.lower() == "actor" :
            for i in self.credits.json().get('cast'):
                self.actdict[i.get('title'), i.get('release_date'), i.get('id')] = i.get('id')
            for i in self.actdict:
                self.imdbid = requests.get("http://api.themoviedb.org/3/movie/" + str(self.actdict[i]) + 
                                      "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338").json().get('imdb_id')
                temp = requests.get("http://www.omdbapi.com/?i=" + self.imdbid).json()
                self.imdbdict[i] = temp.get('imdbRating'), temp.get('imdbVotes')
            for i in self.imdbdict:
                if self.imdbdict[i] != ("N/A", "N/A") and self.imdbdict[i] != (None, None):
                    if int(str(self.imdbdict[i][1].replace(",",""))) > 5000:
                        self.imdbdict2[i] = float(str(self.imdbdict[i][0]))
            self.imdbdict2 = sorted(self.imdbdict2, key=lambda key: float(str(self.imdbdict2[key])), reverse = True)
            for i in range(0, min(len(self.imdbdict2), 15)):
                title = self.imdbdict2[i][0]
                year = self.imdbdict2[i][1][0:4]
                label = title + "\n" + "Year: " + year
                tmdb = self.imdbdict2[i][2]
                button = wx.Button(self, -1, label)
                button.myname = tmdb
                button.Bind(wx.EVT_BUTTON, self.onButton)
                vsizer.Add(button, 1, wx.EXPAND)
        else :
            for i in self.credits.json().get('crew'):
                if i.get('job') == "Director":
                    self.dirdict[i.get('title'), i.get('release_date'), i.get('id')] = i.get('id')
            for i in self.dirdict:
                self.imdbid = requests.get("http://api.themoviedb.org/3/movie/" + str(self.dirdict[i]) + 
                                      "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338").json().get('imdb_id')
                temp = requests.get("http://www.omdbapi.com/?i=" + self.imdbid).json()
                self.imdbdict[i] = temp.get('imdbRating'), temp.get('imdbVotes')
            for i in self.imdbdict:
                if self.imdbdict[i] != ("N/A", "N/A") and self.imdbdict[i] != (None, None):
                    if int(str(self.imdbdict[i][1].replace(",",""))) > 5000:
                        self.imdbdict2[i] = float(str(self.imdbdict[i][0]))
            self.imdbdict2 = sorted(self.imdbdict2, key=lambda key: float(str(self.imdbdict2[key])), reverse = True)
            for i in range(0, min(len(self.imdbdict2), 15)):
                title = self.imdbdict2[i][0]
                year = self.imdbdict2[i][1][0:4]
                label = title + "\n" + "Year: " + year
                tmdb = self.imdbdict2[i][2]
                button = wx.Button(self, -1, label)
                button.myname = tmdb
                button.Bind(wx.EVT_BUTTON, self.onButton)
                vsizer.Add(button, 1, wx.EXPAND)
        hsizer1.Add(vsizer,.1,wx.EXPAND)
        self.SetSizer(hsizer1)
        hsizer1.Fit(self)  
    
    def onButton(self, event):
        name = event.GetEventObject().myname

        get_imdb_rec = requests.get("http://api.themoviedb.org/3/movie/" \
                                    + str(name) + \
                                    "?api_key=53ccaeeec873e469b9095c922f50356c&tt0120338")
        
        self.imdb_id = get_imdb_rec.json().get('imdb_id')
        get_imdb_rating = requests.get("http://www.omdbapi.com/?i=" + self.imdb_id)
        imdb_rating = get_imdb_rating.json().get('imdbRating')
        self.buttons[0][1].SetLabel(imdb_rating)
        
        
        get_rt_rec = requests.get("http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?id=" \
                                  + self.imdb_id[2:] + 
                                  "&type=imdb&apikey=zst8y6gxzjsckez2tautu6xk");
        try:
            rt_critics = str(get_rt_rec.json().get('ratings').get('critics_score'))
            rt_audience = str(get_rt_rec.json().get('ratings').get('audience_score'))
            rt_label = "Critics: " + rt_critics + "%" + "\n" + "Audience: " + rt_audience + "%"
            self.buttons[1][1].SetLabel(rt_label)
        except AttributeError:
            wx.MessageBox('No Rotten Tomatoes data found!', 'Error', wx.OK)
            self.buttons[1][1].SetLabel("")
        meta_rating = get_imdb_rating.json().get("Metascore")
        self.buttons[2][1].SetLabel(meta_rating)
        self.movie_info_dict['imdb_id'] = self.imdb_id
                
def main():
    ''' Create an app instance and a top-level frame,
    then run the main loop.'''
    app = wx.App()
    frame = MovieApp(parent=None, id=wx.ID_ANY, title='CIS 192 Project')
    frame.Show(True)
    app.MainLoop()
    

if __name__ == "__main__":
    main()