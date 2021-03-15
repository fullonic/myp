### MYP: A simple and easy way to Map Your Photos by using the photografies GPS metadata

This is a prototype developed back on 2019, which I plan to redesign and finished during the coming months.

The main goal of this project was project on a map all the photos during a travel around Girona region, Catalonia.

#### How to run

```shell
>> docker -f docker-compose-prod.yml up --build

```

Even though there is any notorious difference from the environment configuration from development and production, the production compose have nginx setup as a web server which gives a better performance.

### Current basic features

- Ability to get photograph GPS metadata and project photos in a map
- Get geographical information from a GPS track (currently only supports .gpx) and insert it to photography metadata

### Future features

- Allow users to manual add geographical information to a photography
- Create a notification system to alert users when the process is done
- Inform users about possible errors
- Add centralized logging system
- Separate backend from frontend
- Improve map style
- and more ...

#### How it works
()[gif_1.gif]