### MYP: A simple and easy way to Map Your Photos by using the photo GPS metadata

This is a prototype developed back on 2019, which I plan to redesign and finish during the coming months.

The main goal of this project was to map all the photos during a travel around Girona region, Catalonia.

#### How to run

```shell
>> docker -f docker-compose.yml up --build

```

App will be available on visit: http://localhost/:5001

### Current basic features

- Ability to get photography GPS metadata and project photos in a map.
- Get geographical information from a GPS track (currently only supports .gpx) and insert it to photography metadata

### Future features

- Allow users to manually add geographical information to a specific photography
- Create a notification system to alert users when the process is done
- Inform users about possible errors
- Add centralized logging system
- Separate backend from frontend
- Improve map style
- and more ...

## How it works

### Create a map by using geographical information extracted from photo metadata

![Create project photos on map using GPS metadata](service_mapping.gif)

### Create a map by extracting geographical information from a GPS track file

![Add GPS information from GPS track](service_by_tag.gif)
