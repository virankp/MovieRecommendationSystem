from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time


class Images():
    def __init__(self):
        self.image_directory  ="C:\\Users\\viran\\Desktop\\Coursework\\Technical Solution\\Images"


    def frame_image(self, image_frame, image, width, height, row_no, column_no):
        image = image.resize((width, height), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label = Label(image_frame, image = image)
        image_label.image = image
        image_label.grid(row = row_no, column = column_no)

    def soup_image(self, URL, movie_name, image_frame, width, height, row_no, column_no):
        movie_name = movie_name.lower()
        response = request.urlopen(URL)
        soup = BeautifulSoup(response, 'html.parser')
        if os.path.exists(self.image_directory+"\\"+movie_name+'.png') == False:        
            image_place = soup.find('div', {'class':'movie-thumbnail-wrap'})
            images = image_place.find('img')
            request.urlretrieve(images['data-src'], self.image_directory + "\\" + movie_name + '.png')
        else:
            print("movie already exists")

        image = Image.open(self.image_directory + "\\" + movie_name + ".png")
        self.frame_image(frame, image_frame, image, width, height, row_no, column_no)

    def get_image(self, frame, movie_name, row_no, column_no):
        movie_name = movie_name.lower()
        current_directory = self.image_directory + "\\" + movie_name + ".png"
        if self.image_directory.isfile(current_directory) == True:
            image = Image.open(current_directory)
            self.frame_image(frame, image, 75, 113, row_no, column_no)
        else:        
            movie_nameURL = re.sub(r"[^a-zA-Z0-9]+", ' ', movie_name)
            movie_nameURL = movie_nameURL.replace(" ", "_")
            URL = 'https://www.rottentomatoes.com/m/' + movie_nameURL
            try:
                print("TRY STATEMENT")
                self.SoupImage(URL, movie_name, frame, 75, 113, row_no, column_no)
            except:
                try:
                    print("EXCEPT STATEMENT")
                    DRIVER_PATH = "C:\\Users\\viran\\Desktop\\Coursework\\Scraping\\chromedriver_win32\\chromedriver.exe"
                    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
                    movie_nameURL = urllib.parse.quote(movie_name)
                    URL = 'https://www.rottentomatoes.com/search/?search=' + movie_nameURL
                    driver.minimize_window()
                    driver.get(URL)
                    time.sleep(2) 
                    content = driver.page_source.encode('utf-8').strip()
                    soup = BeautifulSoup(content, 'html.parser')
                    movie_name = soup.find_all('', {'class':'search__results-item-info-top'})[0]
                    movie_name = movie_name.find_all('a', href=True)[0]
                    movie_name = movie_name.string
                    if "'"  in movie_name:
                        movie_name = movie_name.replace("'", "")
                    movie_nameURL = re.sub(r"[^a-zA-Z0-9]+", ' ', movie_name)
                    movie_nameURL = movie_nameURL.replace(" ", "_")
                    URL = 'https://www.rottentomatoes.com/m/' + movie_nameURL
                    driver.close()
                    self.SoupImage(URL, movie_name, frame, 75, 113, row_no, column_no, padx = 10)
                except:
                    image_label = Label(frame, text = "No Image", font = "Calibri 11")
                    image_label.grid(row = row_no, column = column_no, padx = 10)

    def random_image(self, image_frame, row_no, column_no):
        image = random.choice(os.listdir(self.image_directory))
        image = self.image_directory + "\\" + image
        image = Image.open(image)
        frame_image(image_frame, image, 200, 300, row_no, column_no)

    def update_folder(self):
        number_images = len([image for image in os.listdir(self.image_directory) if os.path.isfile(os.path.join(self.image_directory, image))])
        if number_images > 100:
            all_images = (os.path.join(self.image_directory, image) for image in os.listdir(self.image_directory))
            all_images = ((os.stat(path), path) for path in all_images)
            all_images = ((stat[ST_CTIME], path) for stat, path in all_images if S_ISREG(stat[ST_MODE]))
            all_images = sorted(all_images)
            for image in range(10):
                os.remove(all_images[image][1])

        for image_name in os.listdir(self.image_directory):
            if image_name.endswith('.png') != True:
                os.remove(image_directory + '\\' + image_name)
                time.sleep(2)

image_stuff = Images()
image_stuff.update_folder()
