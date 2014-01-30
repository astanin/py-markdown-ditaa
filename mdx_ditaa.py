import ctypes
import os
import subprocess
import tempfile
import zlib


from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension


# or "java -jar /path/to/ditaa.jar {infile} {outfile} --overwrite"
DITAA_CMD = "ditaa {infile} {outfile} --overwrite"


def generate_diagram(plaintext):
    """Run ditaa with plaintext input.
    Return filename of the generated image.
    """
    imgfname = "diagram-%x.png" % (ctypes.c_uint32(zlib.adler32(plaintext)).value)
    srcfd, srcfname = tempfile.mkstemp(prefix="ditaasrc", text=True)
    outfd, outfname = tempfile.mkstemp(prefix="ditaaout", text=True)
    os.write(srcfd, plaintext)
    os.close(srcfd)
    try:
        cmd = DITAA_CMD.format(infile=srcfname, outfile=imgfname).split()
        with os.fdopen(outfd, "rw") as out:
            retval = subprocess.check_call(cmd, stdout=out)
        return imgfname
    except:
        return None
    finally:
        os.unlink(srcfname)
        os.unlink(outfname)


class DitaaPreprocessor(Preprocessor):
    def run(self, lines):
        START_TAG = "```ditaa"
        END_TAG = "```"
        new_lines = []
        ditaa_prefix = ""
        ditaa_lines = []
        in_diagram = False
        for ln in lines:
            if in_diagram:  # lines of a diagram
                if ln == ditaa_prefix + END_TAG:
                    # strip line prefix if any (whitespace, bird marks)
                    plen = len(ditaa_prefix)
                    ditaa_lines = [dln[plen:] for dln in ditaa_lines]
                    ditaa_code = "\n".join(ditaa_lines)
                    filename = generate_diagram(ditaa_code)
                    if filename:
                        new_lines.append(ditaa_prefix + "![%s](%s)" % (filename, filename))
                    else:
                        md_code = [ditaa_prefix + "    " + dln for dln in ditaa_lines]
                        new_lines.extend([""] + md_code + [""])
                    in_diagram = False
                    ditaa_lines = []
                else:
                    ditaa_lines.append(ln)
            else:  # normal lines
                start = ln.find(START_TAG)
                prefix = ln[:start] if start >= 0 else ""
                # code block may be nested within a list item or a blockquote
                if start >= 0 and ln.endswith(START_TAG) and not prefix.strip(" \t>"):
                    in_diagram = True
                    ditaa_prefix = prefix
                else:
                    new_lines.append(ln)
        return new_lines


class DitaaExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        location = "<fenced_code" if ("fenced_code" in md.preprocessors) else "_begin"
        md.preprocessors.add("ditaa", DitaaPreprocessor(md), location)


def makeExtension(configs=None):
    return DitaaExtension(configs=configs)
