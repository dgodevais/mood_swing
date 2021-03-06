# mood_swing
An Alexa app that responds to your mood using music and hue lighting.

Note that this app does NOT require you to have a server running at home. Everything is triggered via IFTTT api calls.

[See YouTube app demo video here](https://youtu.be/Mb2C52gFPsM)

# Work in progress:
Dynamically respond to emotions with different lights and music.

Note: unfortunatley, spotify api is limited to 30 second previews (not enough time).

# Required materials
* [Amazon Echo/Dot](https://www.amazon.com/dp/product/B00X4WHP5E/ref=EchoCP_dt_tile_text)
* [Hue Smart Lights](https://www.amazon.com/gp/product/B06Y3QXSGX/ref=oh_aui_search_detailpage?ie=UTF8&psc=1)
* [An IFTTT Account](https://ifttt.com/discover)
* [An Amazon Developer Account](https://developer.amazon.com/)

# Getting Started
1. [Follow the steps outlined in this tutorial](https://developer.amazon.com/blogs/post/8e8ad73a-99e9-4c0f-a7b3-60f92287b0bf/new-alexa-tutorial-deploy-flask-ask-skills-to-aws-lambda-with-zappa)
2. [Use this tool to get music links](https://www.wonderplugin.com/online-tools/google-drive-direct-link-generator/)
3. [Check out this awesome framework for Serverless Python](https://github.com/Miserlou/Zappa)

# Config?
I use a yaml file which looks something like this:
```
secrets:
    client_id: {some_client_id}...

music:
    {mood}_url: {stream_url}...

ifttt:
    {mood_url}: {ifttt_url}
```
