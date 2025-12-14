from html.parser import HTMLParser


def format_text(text: str) -> str:
    class SelectiveStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.result = []
            self.stack = []  # Tracks open allowed tags

        def handle_starttag(self, tag, attrs):
            tag = tag.lower()
            attrs_dict = {k.lower(): v for k, v in attrs if k is not None}

            allowed = False
            if tag in {
                "b",
                "strong",
                "i",
                "em",
                "u",
                "ins",
                "s",
                "strike",
                "del",
                "code",
                "pre",
                "blockquote",
                "tg-spoiler",
            }:
                allowed = True
            elif tag == "a" and "href" in attrs_dict:
                allowed = True
            elif tag == "span" and attrs_dict.get("class") == "tg-spoiler":
                allowed = True
            elif tag == "tg-emoji" and "emoji-id" in attrs_dict:
                allowed = True

            if allowed:
                # Rebuild the tag with original attribute formatting (approx)
                attr_parts = []
                for k, v in attrs:
                    if v is None:
                        attr_parts.append(k)
                    else:
                        attr_parts.append(f'{k}="{v}"')
                attr_str = (" " + " ".join(attr_parts)) if attr_parts else ""
                self.result.append(f"<{tag}{attr_str}>")
                self.stack.append(tag)

        def handle_endtag(self, tag):
            tag = tag.lower()
            # Only output closing if it matches an open allowed tag
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
                self.result.append(f"</{tag}>")

        def handle_data(self, data):
            self.result.append(data)

        def handle_entityref(self, name):
            self.result.append(f"&{name};")

        def handle_charref(self, name):
            self.result.append(f"&#{name};")

        # Comments, PIs, etc., are ignored/skipped

        def get_cleaned(self):
            return "".join(self.result)

    text = text.replace("<br>", "\n")
    text = text.replace("\n\n\n", "\n\n")

    parser = SelectiveStripper()
    parser.feed(text)
    parser.close()
    return parser.get_cleaned()
