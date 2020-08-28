# Log of digging into the code of mark2cure


After failing to install mark2cure (see log in the end), I
decided to explore the repository to at least grasp the
relevant bits of code. 


## settings.py

The user interface seems to be coded using the [Django framework] (https://www.djangoproject.com/).
Django is marketed to be a framework "for perfectionists with deadlines". 



it has some words for flatter: 
POSTIVE_FLATTER = ['Bravo', 'Wow', 'Super', 'Terrific', 'Cool', 'Amazing', 'Superb', 'Brilliant', 'Fantastic', 'Fabulous', 'You\'re a Champion', 'Well done', 'You rock', 'Great job', 'Tip top', 'Good thinking', 'Keep it up', 'Way to go', 'Right on', 'Top stuff', 'Take a bow', 'Unreal', 'Impressed', 'Great stuff', 'Awesome', 'Nice going', 'Very Creative', 'Thank You', 'Beautiful', 'Very proud', 'Good for you', 'Give me five', 'You make me happy', 'A+', 'A++', 'AA+', 'Fab', 'Rad', 'A+++', 'AAA+', 'A-OK', 'Best', 'Cool', 'Deal', 'Fast', 'Fine', 'Item', 'Nice', 'Safe', 'Thx!', 'WOW!', 'Prime', 'Solid', 'Super', 'Sweet', 'Thanx', 'Whoa!', 'Groovy', 'Honest', 'Speedy', 'Superb', 'Sweeet', 'Thanks', 'Zowie!', 'Amazing', 'Awesome', 'Quality', 'Service', 'Sweeeet', 'Glorious', 'Stunning', 'Superior', 'The Best', 'The Bomb', 'Thrilled', 'Way Cool', 'Brilliant', 'Competent', 'Delighted', 'Excellent', 'Exquisite', 'Marvelous', 'Overjoyed', 'Satisfied', 'Thank You', 'Top Notch', 'Unrivaled', 'Wonderful', 'A Home Run', 'Astounding', 'Delightful', 'Impressive', 'Incredible', 'Super Cool', 'Super Fast', 'Supersonic', 'Astonishing', 'Fascinating', 'Interesting', 'Magnificent', 'No Problems', 'Outstanding', 'Splendorous', 'Trustworthy', 'Unsurpassed', 'Wicked Cool', 'Breathtaking', 'Looking Good', 'Overwhelming!', 'Unbelievable!', 'Awe Inspiring', 'Lickety Split', 'Splendiferous', 'Thanks A Ton!', 'Extremely Cool', 'Satisfied 100%', 'Extremely Happy', 'Great Condition', 'Above And Beyond', 'State Of The Art', 'Thanks A Million!', 'Unbelievably Cool', 'Expertly Described', 'Extremely Satisfied', 'Great Communication', 'Greatly Appreciated', 'Beyond My Wildest Dreams', 'Supercalifragilisticexpialidocious', 'Thank You! Thank You! Thank You!']
SUPPORT_FLATTER = ['You can do it', 'Nice Try', 'Don\'t give up', 'Every bit counts', 'Thank you', 'Keep going', 'You can do better than that']


It has code for usernames. 

## userprofile folder

### models.py

It has many functions to prepare a user profile


## document folder

### managers.py 

References to PubTator and PubTator's API. 

## task folder

### models.py

Contains different task names and difficulty levels: 

levels = ["Basic", "Disease Marking", "Disease Advanced", "Disease Matching", "Intermediate", "Proficient", "Advanced", "Expert", "Expert", "Expert"]

levels = ["Beginner", "Medium", "Expert", "Expert", "Expert"]


Classes related to Entity Recognition tasks:

class Task(models.Model):
    """This is an ER Quest, tracks whose completed it and what documents are contained within
        the Quest
    """

### task/ner folder

Contains the code for getting a score via comparison of two players.



# Log of installation of mark2cure

Trying to install it as described [here](https://github.com/SuLab/mark2cure/blob/master/Setup.md)

I will try and set up mark2cure running locally (I'm running Ubuntu 18.04).








# Dependencies
Okay, so first I'll run a series of commands at the root of the repository. I might have installed one or two of the required packages before (I had a run at this months ago, albeit without a log).

The setup file makes it clear REMEMBER THE PASSWORD USED FOR INSTALLING MySQL!


```
sudo apt update
sudo apt upgrade
```

A lot of packages are upgraded. 

It was taking forever to install something called `93% [15 zotero 1.758 kB/63,1 MB 3%]` . I cut it (`ctrl-c`) and went on.  

```
sudo apt install build-essential python python-dev python-pip python-virtualenv libmysqlclient-dev git-core nginx supervisor rabbitmq-server graphviz libgraphviz-dev pkg-config libncurses5-dev npm ruby-dev
```

Now I got this error:

```The following packages have unmet dependencies:

npm : Depends: node-gyp (>= 0.10.9) but it is not going to be installed 

Unable to correct problems, you have held broken packages.```

I try to install node-gyp. 

"sudo aptitude node-gyp" suggests: 

```

Remove the following packages:                                                                     │
1)      libmysqlclient-dev          │
2)      libssl-dev 

```

Doesn't look good. But here we go. Later I handle the problems of removing those packages. 

Now I run

```
sudo pip3 install -r -requirements.txt
```

This is a file with a bunch of python dependencies. 

I got an error:

ImportError: cannot import name 'Feature'

According to [this GitHub issue](https://github.com/pypa/setuptools/issues/2017) it is a problem with the setuptools version. I will try the solution raised there: `pip3 install setuptools == 45`

I got an error: 

ERROR: launchpadlib 1.10.6 requires testresources, which is not installed.

ERROR: mordecai 2.0.3 has requirement spacy<2.1.0,>=2.0.3, but you'll have spacy 2.3.2 which is incompatible

Now when I run the requirements installation I get a different error. 
It tells me that "Features are deprecated and will be removed in a later version."

I got an error: 

AttributeError: 'Distribution' object has no attribute 'with_speedups'  


This looks just too much of a problem. 

I will figure out later which python3 packages are missing. 

```
sudo pip3 install nltk
sudo npm install gulp-cli -g
sudo npm install gulp -D
sudo npm install gulp-compass gulp-if gulp-livereload gulp-clean-css gulp-csso gulp-sass gulp-rename tiny-lr segfault-handler

sudo npm install -g bower
sudo bower install
```

Now I got an error: 
Since bower is a user command, there is no need to execute it with superuser permissions.

I tried

```
sudo bower install --allow-root
```

And now I got: 
bower ENOENT        No bower.json present 


I will skip it. 

Now some Ruby packages:

```
sudo gem update --system
sudo gem install compass
```

ERROR:  Error installing compass:                                          
        ERROR: Failed to build gem native extension.  


I ran: 
```
sudo apt-get install ruby-dev
sudo gem install compass
sudo ln -s /usr/bin/nodejs /usr/bin/node
```
And error: 

ln: failed to create symbolic link '/usr/bin/node': File exists




# Local setup

I note that I had installed MySQL before, but I do not know my password.

The setup mentions "if you get ENTREZ_EMAIL from Max, you need to put that here as well." I have no idea what or who is Max.


I tried running `gulp` as suggested and got: 

", you need to put that here as well"

Error: Cannot find module 'gulp-load-plugins'

Apparently gulp-util is deprecated, so I had failed to `npm install` it earlier. 

N deprecated gulp-util@3.0.8: gulp-util is deprecated

So this is a hard failure on resetting the system :(


# Problems ignored for the moment 

## Dependencies

Problems in the requirements python packages:
AttributeError: 'Distribution' object has no attribute 'with_speedups'  


```
sudo bower install --allow-root
```

And now I got: 
bower ENOENT        No bower.json present 

