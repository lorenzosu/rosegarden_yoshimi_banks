# rosegarden_yoshimi_banks

Yoshimi banks definition for Rosegarden - python generation script

Example:
``./rgd_yoshimi_banks.py /usr/local/share/yoshimi/banks/ Yoshimi.rgd``

Assuming the python file is executable

Extended Programs (i.e. greater than midi 127 (128 in Rosegarden and Yoshimi) are supported and 'just work' now!

To make this work in Yoshimi the following settings are needed in the MIDI CC
tab:

```
Bank Root Change: Off
Bank Change: MSB

Enable Program Change: [Selected]
```

See screenshot:

<img src="https://raw.githubusercontent.com/lorenzosu/rosegarden_yoshimi_banks/master/yoshimi_settings_screenshot.png" alt="yoshimi screenshot" width="50%">

Short demo video:

<video width="90%" src="https://github.com/lorenzosu/rosegarden_yoshimi_banks/assets/463937/3ddf9017-2a7c-43d2-83d4-5f9ac855d6c8">

Direct Link to Video:
[https://github.com/lorenzosu/rosegarden_yoshimi_banks/assets/463937/3ddf9017-2a7c-43d2-83d4-5f9ac855d6c8](https://github.com/lorenzosu/rosegarden_yoshimi_banks/assets/463937/3ddf9017-2a7c-43d2-83d4-5f9ac855d6c8)
