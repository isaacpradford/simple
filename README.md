# Welcome to Simple
## A simple idle game about simple math
Check it out [here!](https://simple-bwhx.onrender.com/)

#### Intro
I've always loved idle games (especially games like Cookie Clicker that I could play in my middle school computer lab). But recently, I've felt like the internet just isn't as fun for kids anymore. Not because of weirdos or anything, but with the fall of flash games, there's just not as many fun things to do on the internet (other than scroll TikTok or Twitter, which is still p fun). About a month ago, I decided it could be a good project to try to build my own, basic idle game, and that's how we got here.

This is my first larger project with Django, and so there were a lot of learning curves, but for the most part, I'm happy with how it's turned out. There's some bugs here and there, like how the user will sometimes just start getting double points when they click (it's a feature not a bug). I'll iron out a lot of them, but for now, I'm happy with where it's at. 

#### How does it work?
In a basic idle game, the user earns points when real world time passes. Then, in some games, there's also a button for the user to click to accelerate their point earning. This game works like that. You click, time passes, you get points, you buy new numbers, you repeat the process and hopefully get a high score!

As for the technical side, this project was built as a full-stack Django/Bootstrap project with a postgresql database, all hosted on Render. It utilizes server-side rendering to return pages to the user and AJAX to return the users new score when something is clicked, bought, or sold. I initially wrote (and finished) this project using a django rest-api and a React FE, but decided I wanted to learn SSR better. Also, React / Javascript has a bigint limit of 9,007,199,254,740,991, which usually would be big enough for any web application, but when you're playing a clicker Idle game, 9 quadrillion just wasn't going to cut it. Python is better at handling large ints though, and is capable of giving us those juicier numbers, and by utilizing this with PostgreSQLs digit data type, numbers now have a limit of 500 digits / 1 Quingentillion!

While this system works great for the silly little game that this is, there is one large issue with it:

#### The main bug

On the technical side, the backend is what actually knows the users score, while the FE just estimates it using a 15 second (or less) timer. Based on the users purchased time, the server will figure out how many 15 second (or lower) increments have passed between now and the last time the user updated the score, and then will take that number of time increments and multiply it by the sum total of all the users numbers. This was a clever workaround to calculating their score with something more intense (if I do say so myself). 

This works great, however, there's one main problem with it: the FE score estimation. None of my playtesters noticed until I pointed it out, but sometimes, the score for the FE won't be the same as the accurate score on the BE. Often, it will be off by 1 or 2 increments, and they'll suddenly gain / lose points if they reload the page. This can happen for a variety of reasons, but at the heart of it, when the user loads into a game, the timer starts at 0 / 15s seconds. On the server though, there might only be 6 seconds left until the next increment. This means that users score might be off by a +/- increment, which isn't a huge deal, but as a developer, it feels bad just to leave a bug like that in the game. In addition, sometimes the FE is just a bit buggy, and so the FE timer just isn't entirely trustworthy.

The next step to fix this would be going all in and adding webhooks / cron jobs to let a server update every users score at the same time. This would probably be more fair from a gameplay perspective too, but at the moment, I just don't have the resources to host the server needed for that. So for now, this is the best we got. 


#### Next Steps:
While I think the app is great as it is, there are a couple of things that I'd love to add / fix. 

1. Achievements
   Pretty self explanatory. I think achievements would give something to work towards beyond just seeing the number go up
2. Purchasable Themes
   I want to add a way to purchase/unlock color themes for the app that would translate between games. Similar to an achievement, I'd love to be able to give a reward for progressing!



#### And that's it!
If you've made it this far, thanks for reading my rambling and checking out Simple. If you want to help keep the servers running, consider clicking the venmo link [here:]([https://simple-bwhx.onrender.com/](https://account.venmo.com/payment-link?amount=5.00&note=Thanks%20for%20the%20game&recipients=isaac-radford&txn=pay). Anything would be greatly appreciated 🙏🙏🙏

Have fun, and happy clicking~
