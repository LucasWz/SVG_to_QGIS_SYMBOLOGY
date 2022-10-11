from typing import Dict
from bs4 import BeautifulSoup as bs
import yaml
from pathlib import Path


class PathNotExists(Exception):
    pass


class ExitProgram(Exception):
    pass


class XMLAttributeError(Exception):
    pass


def load_yaml(path: str) -> dict:
    """Load yaml data from path."""
    with open(path, mode="r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    return data


def read_xml_soup(path) -> bs:
    """Read file and convert it to BeautifulSoup object with 'xml' parser."""
    with open(path, "r") as f:
        data = f.read()
    return bs(data, "xml")


def add_attributes(soup: bs, id_: str, attrs: Dict[str, str]) -> None:
    """
    Parse soup object to find tag that contains attribute 'id' equals 'id_'.
    Check if this tag is named 'path' then loop trough adding attributes
    and values in place.
    """

    element = soup.find(id=id_)
    if element:
        if element.name != "path":
            element = element.find("path")
            if not element:
                raise XMLAttributeError(f"Attribute id='{id_}' has no path.")

        for attr, value in attrs.items():
            element[attr] = value

    else:
        raise XMLAttributeError(f"Attribute id='{id_}' not found in SVG file.")


def write_xml(soup: bs, path: str) -> None:
    """Write prettified BeautifulSoup object in file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())


def make_svg_qgis_readable() -> None:
    """Add attributes to SVG file to use them as variables in QGis."""

    # Define yaml path and distant svg path with source svg path
    # given as user input.
    src_svg_path = Path(input("Enter a svg path to convert or quit (q) : "))
    if str(src_svg_path) == "q":
        raise ExitProgram()

    elif not src_svg_path.exists():
        raise PathNotExists(f"Source SVG path '{src_svg_path}' not exists.")

    attrs_path = src_svg_path.parent / f"{src_svg_path.stem}.yml"
    if not attrs_path.exists():
        raise PathNotExists(f"YAML path '{attrs_path}' not exists.")

    dst_svg_path = src_svg_path.parent / f"{src_svg_path.stem}_qgis.svg"

    # Load ids, attribues and values from yaml file. Parse source SVG and write
    # them in a new SVG file.
    parameters = load_yaml(attrs_path)
    svg_soup = read_xml_soup(src_svg_path)

    for id_, attrs in parameters.items():
        add_attributes(svg_soup, id_, attrs)

    write_xml(svg_soup, dst_svg_path)

    return dst_svg_path


def main():

    print("#" * 79)
    print("QGIS' SVG SYMBOL CONVERTER".center(79))
    print()

    while True:
        try:
            dst_svg_path = make_svg_qgis_readable()

        except ExitProgram:
            print("Exit program.")
            print("#" * 79)
            break

        except PathNotExists as e:
            print(f"-> {e} Please retry with a new path or quit.")

        except XMLAttributeError as e:
            print(f"-> {e} Please check your attributes and retry or quit.")

        except Exception as e:
            print(f"-> Unexpected error occured :\n{e}")

        else:
            print(f"-> QGis SVG file successfully created : '{dst_svg_path}'.")


if __name__ == "__main__":
    main()
