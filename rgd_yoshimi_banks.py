#!/usr/bin/env python
"""
A script to generate Rosegarden .rgd instrument files pasring the direcory
structure of Yoshimi banks
"""
import os
import argparse
import io
import tempfile
import gzip
import shutil
import logging
import xml.etree.ElementTree as ET

XML_HEADER_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rosegarden-data>
"""
XML_TEMPLATE_STRING = """<rosegarden-data version="4-0.9.1">
  <studio thrufilter="0" recordfilter="0">
    <device id="0" name="Yoshimi" direction="play" variation="LSB" type="midi">
      <librarian name="Lorenzo Sutton" email="lorenzofsutton@gmail.com"/>
      <!-- Controls (midi controllers). These are sane defaults for Yoshimi -->
      <controls>
        <control name="Pan" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="10" colourindex="2" ipbposition="0"/>
        <control name="Chorus" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="93" colourindex="3" ipbposition="1"/>
        <control name="Volume" type="controller" description="&lt;none&gt;" min="0" max="127" default="100" controllervalue="7" colourindex="1" ipbposition="2"/>
        <control name="Reverb" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="91" colourindex="3" ipbposition="3"/>
        <control name="Sustain" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="64" colourindex="4" ipbposition="-1"/>
        <control name="Expression" type="controller" description="&lt;none&gt;" min="0" max="127" default="100" controllervalue="11" colourindex="2" ipbposition="-1"/>
        <control name="Modulation" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="1" colourindex="4" ipbposition="-1"/>
        <control name="Cutoff Freq" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="74" colourindex="2" ipbposition="2"/>
        <control name="Resonance" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="71" colourindex="2" ipbposition="2"/>
        <control name="Attack time" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="73" colourindex="2" ipbposition="2"/>
        <control name="Release time" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="72" colourindex="2" ipbposition="2"/>
        <control name="PitchBend" type="pitchbend" description="&lt;none&gt;" min="0" max="16383" default="8192" controllervalue="1" colourindex="4" ipbposition="-1"/>
      </controls>
      <!-- Begin BANK section -->
    </device>
  </studio>
</rosegarden-data>
"""


def make_bank_xml_element(bank_name, bank_num):
    """
    takes the bank name and the number (as in yoshimi) and creates
    <bank> and all the <program> elements for each bank
    """
    # XML template stub for a <bank> element. note name and msb are empty now
    b_el = ET.fromstring('<bank name="" percussion="false" msb="" lsb="0"/>')

    b_el.attrib['name'] = bank_name
    b_el.attrib['msb'] = bank_num

    prog_template = '<program id="" name="" category=""/>'
    # Parse the bank directory searching for .xiz (instrument) files
    # We need to sort the files in order to have them correctly listed in the
    # XML file
    file_list = sorted(os.listdir(bank_dir))
    for file in file_list:
        if file.find('.xiz') < 0:
            continue
        # Try to extract number and name based on the filename
        number = str(int(file[0:4]) - 1)
        try:
            name = file[file.index('-') + 1:file.index('.xiz')]
            name = name.replace("_", " ")
        except ValueError:
            # something wrong with the path name?
            continue
        p_el = ET.fromstring(prog_template)
        p_el.attrib['id'] = number
        p_el.attrib['name'] = name
        p_el.attrib['category'] = bank_name
        b_el.append(p_el)

    # We return the whole <bank> element with all of its <program> children
    return b_el

def parse_arguments():
    """ Parse the command line arguments and returned the parsed argparse """
    # Parse arguments in particular root dir for banks and the output rgd file
    arg_parser = argparse.ArgumentParser(
        description=(
            "A script to generate Rosegarden .rgd instrument files pasring "
            "the directory structure of Yoshimi banks"
        )
    )
    arg_parser.add_argument("bank_root_dir")
    arg_parser.add_argument("output_rgd_file")
    arg_parser.add_argument(
        '--xml',
        action='store_true',
        help=(
            "also output the actual generated xml file for debugging pourposes"
        )
    )
    return arg_parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO)

    args = parse_arguments()

    bank_root_dir = args.bank_root_dir
    out_file = args.output_rgd_file

    logging.info("Searching and parsing banks in %s", bank_root_dir)

    # Set-up XML file including the header template with initial <control> tags
    xml_string = io.StringIO(XML_TEMPLATE_STRING)
    # The parser stuff just to preserve comments in the template string :|
    # See docs for xml.etree.ElementTree.TreeBuilder
    tree = ET.parse(
        xml_string,
        parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        )
    # The root should be the <rosegarden-data> element
    root = tree.getroot()
    # All banks will be <bank> elements under the <device> element
    device_el = root.findall(".//device")[0]

    # Parse the bank root directory and find banks (1 dir = 1 bank)
    bank_list = sorted(os.listdir(bank_root_dir))

    # Currently the default official banks released with Yoshimi seem to go in
    # multiples of 5. So for example 5. Arpeggios, 10. Bass and so on...
    # we increase the number of 5 and assign that as the MIDI bank MSB
    # This 'interval' is defined by the STEP variable here.
    STEP = 5
    THIS_NUM = 0
    logging.info("Generating XML file structure...")

    # Iterate over the list of banks (i.e. the directories)
    for b in bank_list:
        THIS_NUM += STEP
        bank_dir = os.path.join(bank_root_dir, b)
        this_name = os.path.split(bank_dir)[1]
        new_bank_el = make_bank_xml_element(
            this_name,
            str(THIS_NUM)
            )
        comment = ET.Comment(f' Bank Name: {this_name} - Bank num: {THIS_NUM}')
        device_el.insert(THIS_NUM, comment)
        device_el.append(new_bank_el)

    # Generate the complete XML string including pretty indentation
    ET.indent(root)
    eltree_string = ET.tostring(root, encoding="utf-8")
    output_string = XML_HEADER_STRING + eltree_string.decode('utf-8')

    # We store the XML file to a temp dir as it has to be packaged in a gzip
    # Optionally, with the --xml flag we keep the XML file (see below)
    temp_dir = tempfile.gettempdir()
    xml_file = os.path.join(temp_dir, "Yoshimi")
    logging.info("Saving to %s", out_file)
    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(output_string)

    # Gzip the xml giving it the name out_file (typically a .rgd file)
    with open(xml_file, 'rb') as f_in, gzip.open(out_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    # If the --xml flag was given also keep and save the uncmopressed XML file
    # useful to debug the xml output e.g. in a text editor
    if args.xml:
        XML_FILE = 'rgd_yoshimi_banks.xml'
        logging.info("Saving debug XML file: %s", XML_FILE)
        shutil.copy(xml_file, os.path.join('.', XML_FILE))
