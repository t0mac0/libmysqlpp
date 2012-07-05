#
#  This file is part of Bakefile (http://www.bakefile.org)
#
#  Copyright (C) 2003-2007 Vaclav Slavik
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#
#  $Id: outmethods.py 1148 2008-01-05 19:55:15Z vaclavslavik $
#
#  Output methods
#

import errors

# --------------------------------------------------------------------------
# mergeBlocks(WithFilelist):
# --------------------------------------------------------------------------

BLOCK_MARK_LEFT = '### begin block '
BLOCK_MARK_RIGHT = ' ###'

def _findBlocks(data, parseHeader = lambda x:(x,None)):
    """Parses the file and finds marked blocks in it. parseHeader function
       is called on every found block name and it returns tuple (name,data),
       where 'name' is the real name of the block and 'data' is additional data
       to be stored together with the entry (e.g. arguments appended to the
       end of header."""
    blocks = {}
    cur = []
    blocks[''] = (cur, None) # special type of block
    for line in data:
        pos = line.find(BLOCK_MARK_LEFT)
        if pos != -1:
            l = line.rstrip()
            if l.endswith(BLOCK_MARK_RIGHT):
                name = l[pos+len(BLOCK_MARK_LEFT):-len(BLOCK_MARK_RIGHT)]
                cur = []
                name, moredata = parseHeader(name)
                blocks[name] = (cur, moredata)
        cur.append(line)
    return blocks


def mergeBlocks(old, new):
    """Detects blocks beginning with '### begin block <blockname>' in the
       file and replaces blocks in the old file with same blocks from the new
       one, if they exist."""
    b_old = _findBlocks(old)
    b_new = _findBlocks(new)

    keys = b_old.keys() + b_new.keys()
    keys.sort()
    
    out = []
    used = {}
    for block in keys:
        if block in used: continue
        if block in b_new:
            out += b_new[block][0]
        else:
            out += b_old[block][0]
        used[block] = 1
   
    return out


def mergeBlocksWithFilelist(old, new):
    """Like mergeBlocks(), but keeps track of which source .bkl files caused
       this output and automatically removes blocks who use-count dropped to
       zero."""
    import re
    import mk
    filename = mk.vars['INPUT_FILE_ARG'].replace('\\', '/') # unix path
    
    def parseFilelist(hdr):
        # the header/name has format "name[list,of,files]" where the list is
        # optional and contains names of input files that use this block
        args_begin = hdr.rfind('[')
        args_end = hdr.rfind(']')
        if args_begin == -1 or args_end == -1:
            return (hdr, [])
        else:
            args=hdr[args_begin+1:args_end]
            return (hdr[:args_begin], args.split(','))
    
    b_old = _findBlocks(old, parseFilelist)
    b_new = _findBlocks(new, parseFilelist)
    
    keys = b_old.keys() + b_new.keys()
    keys.sort()
    
    out = []
    used = {}
    for block in keys:
        if block in used: continue
        if block in b_new:
            if block == '': # special case, just write it out:
                out += b_new[block][0]
                continue
            content = b_new[block][0]
            # append ourselves to the list of block users:
            if block in b_old:
                files = b_old[block][1]
                if filename not in files:
                    files.append(filename)
                    files.sort()
            else:
                files = [filename]
        else:
            content = b_old[block][0]
            # remove ourselves from the list of users:
            files = b_old[block][1]
            if filename in files:
                files.remove(filename)

        # blocks that don't have associated file are obsolete and are removed:
        if len(files) > 0:
            # add filelist to the header:
            list = '%s[%s]' % (block, ','.join(files))
            # replace occurence with header name followed by optional files
            # list with updated files list:
            content[0] = re.sub(r'%s(\[[^]]*\])?' % block, list, content[0])
            # output the result:
            out += content

        used[block] = 1
   
    return out


# --------------------------------------------------------------------------
# insertBetweenMarkers:
# --------------------------------------------------------------------------

def insertBetweenMarkers(old, new):
    """Inserts text between markers (= special meaning lines). 'old' must
       contain firsts and last line of 'new' -- the text between them is
       replaced with 'new'."""

    begin = new[0]
    end = new[-1]

    if begin not in old:
        raise errors.Error('marker %s not present in the file' % repr(begin))
    if end not in old:
        raise errors.Error('marker %s not present in the file' % repr(end))

    out = []
    i = 0
    while i < len(old) and old[i] != begin:
        out.append(old[i])
        i += 1
    while i < len(old) and old[i] != end: i += 1
    i += 1
    out += new
    while i < len(old):
        out.append(old[i])
        i += 1

    return out

