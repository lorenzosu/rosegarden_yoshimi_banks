# rosegarden_yoshimi_banks
Yoshimi banks definition for Rosegarden - python generation script

Example:
```./rgd_yoshimi_banks.py /usr/local/share/yoshimi/banks/ Yoshimi.rgd```

Assuming the python file is executable

Note that Yoshimi's 'extended' programs (i.e. with a number greater than 127)
are not supported at the moment (they will be added but Rosegarden can't
really use them as they would need an additional controller to be sent)

To make this work in Yoshimi the following settings are needed in the MIDI CC
tab:
```
Bank Root Change: Off
Bank Change: MSB

Enable Program Change: [Selected]
```
Short demo video:

https://github.com/lorenzosu/rosegarden_yoshimi_banks/assets/463937/3ddf9017-2a7c-43d2-83d4-5f9ac855d6c8

