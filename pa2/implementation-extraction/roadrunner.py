from html.parser import HTMLParser

PCDATA = '#PCDATA'
COND = '?'
LB = '('
RB = ')'
PLUS = '+'

START_TAG = 'stag'
END_TAG = 'etag'
VALUE = 'value'

## MATCHING ALGORITHM
# works on two objects at the same time
# 1. list of tokens called the sample
# 2. a wrapper
# parses the sample using the wrapper
# when a mismatch is found try to a generalized the wrapper

# 2 types of mismatches:
# string mismatch - different strings in corresponding positions of the wrapper and sample
# tag mismatch - different tags of the wrapper and the sample

# string mismatches used to discover fields #PCDATA

# TAG mismatch
# discover iterators and optionals
# look for optionals with tag mismatches:
#   1. find mismatch and assume it is because of an optional
#   2. in the wrapper and sample piece of html that is not present in the other side
#       check on the other
#   3. TWO STEPS:
#       i) optional pattern location by cross-search
#       ii) wrapper generalization -> pattern "(<IMG src=.../>)?"
# DISCOVERING ITERATORS
# 1. square location by terminal-tag search
#   -> both sample and wrapper contain at least one occurrence
#   -> identify the last token of the square by looking at the token
#   immediately before the mismatch position - terminal tag
#   -> two possibilities
#       -> i) candidate square of the form </ul> ... </li> (not a real square) on the wrapper
#       -> ii) candidate square of the form <li> ... </li> on the sample
#       check both possibilities by searching first the wrapper and then the sample
#       for the occurrences of the terminal tag </li>
# 2. Square matching
#   -> match the candidate square occurrences against some upward portion of the sample (where we find closing tag)
# 3. Wrapper generalization
#   -> search the wrapper for contiguous repeated occurrences of the square around the mismatch region
#  CHECK FIRST FOR ITERATORS, otherwise we can misinterpret them as optionals


class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value


class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._tokens = []

    def handle_starttag(self, tag, attrs):
        # we simplify the algorithm to only include tags
        self._tokens.append(Token(START_TAG, tag))

    def handle_endtag(self, tag):
        self._tokens.append(Token(END_TAG, tag))

    def handle_data(self, data):
        self._tokens.append(Token(VALUE, data))

    def get_tokens(self):
        return self._tokens


def find_square_candidate(tokens, i, terminal_tag):
    while i < len(tokens):
        if tokens[i].value == terminal_tag:
            return i
        i += 1
    return -1


def match_squares(tokens, i, s2_i):
    s1_i = i-1
    while s2_i > i:
        if (tokens[s1_i].token_type == VALUE and tokens[s2_i].token_type == VALUE) or \
                tokens[s1_i].value == tokens[s2_i].value:
            s1_i -= 1
            s2_i -= 1
        else:
            # we found non-matching tags in the square candidate -> it is not a match
            return False
    # found the match for the whole square
    return True


def handle_tag_mismatch(wrapper, sample, i, j):
    # first we discover iterators
    terminal_tag = wrapper[i-1].value
    start_tag_candidate_1 = wrapper[i].value
    start_tag_candidate_2 = sample[j].value

    c1_index = find_square_candidate(wrapper, i, terminal_tag)
    c2_index = find_square_candidate(sample, j, terminal_tag)

    found_square_wrapper = False
    found_square_sample = False
    if c1_index != -1:
        found_square_wrapper = (wrapper, i, c1_index)
    if c2_index != -1 and not found_square_wrapper:
        found_square_sample = match_squares(sample, j, c2_index)

    generalize_wrapper(wrapper, i, c1_index)


def get_wrapper(htmls1, htmls2):
    parser1 = SimpleHTMLParser()
    parser2 = SimpleHTMLParser()
    # tokenize the two html strings
    parser1.feed(htmls1)
    parser2.feed(htmls2)

    wrapper = parser1.get_tokens()
    sample = parser2.get_tokens()

    i, j = 0, 0
    # iterate over the two tokenized htmls
    while i < len(wrapper) and j < len(sample):
        if wrapper[i].token_type == VALUE and sample[i].token_type == VALUE and \
                wrapper[i].value == sample[i].value:  # matching tag of string, we don't do anything
            i += 1
            j += 1
            continue

        if wrapper[i].token_type == sample[j].token_type: # matching token type
            if wrapper[i].token_type == VALUE:  # tokens are values and not tags
                if wrapper[i].value != sample[j].value:  # string mismatch, add #PCDATA
                    wrapper[i].value = PCDATA
            else:
                if wrapper[i].value != sample[j].value: # tag mismatch
                    handle_tag_mismatch(wrapper, sample, i, j)
        else:
            # tag mismatch
            handle_tag_mismatch(wrapper, sample, i, j)

        # move on with the iteration
        i += 1
        j += 1
        continue

    wrapper_str = ""
    for s in wrapper:
        wrapper_str += s + "\n"

    # print the wrapper into a file
    with open(f"overstock_wrapper.txt", "w") as outfile:
        outfile.write(wrapper_str)
