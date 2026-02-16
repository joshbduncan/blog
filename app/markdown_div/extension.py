import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension


def _handle_double_quote(s, t):
    k, v = t.split("=", 1)
    return k, v.strip('"')


def _handle_single_quote(s, t):
    k, v = t.split("=", 1)
    return k, v.strip("'")


def _handle_key_value(s, t):
    return t.split("=", 1)


def _handle_word(s, t):
    if t.startswith("."):
        return ".", t[1:]
    if t.startswith("#"):
        return "id", t[1:]
    return t, t


_scanner = re.Scanner(  # type: ignore
    [
        (r'[^ =]+=".*?"', _handle_double_quote),
        (r"[^ =]+='.*?'", _handle_single_quote),
        (r"[^ =]+=[^ =]+", _handle_key_value),
        (r"[^ =]+", _handle_word),
        (r" ", None),
    ]
)


def get_attrs(str):
    """Parse attribute list and return a list of attribute tuples."""
    return _scanner.scan(str)[0]


class MarkdownDiv(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(MarkdownDivProcessor(md.parser), "box", 175)


class MarkdownDivProcessor(BlockProcessor):
    """Create <div> elements from fenced Markdown blocks.
    Mostly borrowed from https://python-markdown.github.io/extensions/attr_list/

    Fenced block must be as follows:

    <<< #element-id .class1 .class2 data-attribute="test"
    Markdown content to be rendered inside...
    >>>

    """

    RE_FENCE_START = r"^<{3}(.*)\n"
    RE_FENCE_END = r"\n>{3}\s*$"

    def test(self, parent, block):
        """Test to make sure fenced text is found in block"""
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        """Run the regex on the block and construct the div"""
        original_block = blocks[0]

        # get first line of fence
        match = re.match(self.RE_FENCE_START, blocks[0])

        if not match:
            return

        # replace the fence start
        blocks[0] = re.sub(self.RE_FENCE_START, "", blocks[0])

        # find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, "", block)
                # render fenced text inside a new div
                e = etree.SubElement(parent, "div")
                for k, v in get_attrs(match.groups()[0].strip()):
                    cls = e.get("class")
                    if k == ".":
                        if cls:
                            e.set("class", f"{cls} {v}")
                        else:
                            e.set("class", v)
                    else:
                        # assign attr k with v
                        e.set(k, v)
                # parse block text that goes into new div
                self.parser.parseBlocks(e, blocks[0 : block_num + 1])
                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        # no closing fence found so reset everything
        blocks[0] = original_block
        return False
