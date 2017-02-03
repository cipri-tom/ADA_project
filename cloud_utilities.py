import pandas as pd

def process_cat(cat_df, wc, verbose=True):
    """ Given a DataFrame `cat_df` with reviews and ratings for a category, returns `freq_df` DataFrame with positive,
    negative and total frequencies of words in reviews.

    It uses the passed wordcloud `wc` to preprocess the text, including lemattizing, stopwords, collocations and the max
    number of words. So be sure to setup the `wc` correctly before calling.

    [This allows to use same wordcloud with multiple DataFrames]
    """
    import operator
    import time
    t = time.time()

    # 'average' reviews (score == 3) are ignored; they are not that many anyway
    idx_pos = cat_df.overall > 3
    idx_neg = cat_df.overall < 3
    pos_corpus = cat_df[idx_pos].reviewText.str.cat(sep='\n')
    neg_corpus = cat_df[idx_neg].reviewText.str.cat(sep='\n')

    # we want to get the different frequencies for pos / neg
    pos_words = wc.process_text(pos_corpus)
    neg_words = wc.process_text(neg_corpus)
    if verbose: print("Processing done", time.time() - t, flush=True)

    # filter out the least frequent ones; why doesn't `wc.process_text` do this already :| ?
    pos_words = sorted(pos_words.items(), key=operator.itemgetter(1), reverse=True)[:wc.max_words]
    neg_words = sorted(neg_words.items(), key=operator.itemgetter(1), reverse=True)[:wc.max_words]

    # setup DFs for each and merge them
    pos_df = pd.DataFrame.from_records(pos_words, columns=['word', 'pos'], index='word')
    neg_df = pd.DataFrame.from_records(neg_words, columns=['word', 'neg'], index='word')

    freq_df = pd.merge(pos_df, neg_df, how='outer', left_index=True, right_index=True).fillna(0)
    freq_df['total'] = freq_df.pos + freq_df.neg

    return freq_df, idx_pos.sum(), idx_neg.sum()


def score_word(pos, neg, total_pos, total_neg, normalized=True):
    """ Gives the magnitute of the 'feeling' based on frequencies. This is balanced with the total frequencies
        If normalized, returns in [0,1]. Otherwise, in [-1, 1]

        Note:
        -----
        can underflow if very big `total`

        Parameters:
        -----------
        pos      , neg       : frequencies of a word
        total_pos, total_neg : frequencies for each class
    """
    if pos == 0 and neg == 0:
        ratio = 0
    else:
        # scale to account for class imbalance
        pos, neg = pos/total_pos, neg/total_neg
        ratio = (pos - neg) / (pos + neg) # [-1, 1]
    if normalized:
        return (ratio + 1) / 2            # [0, 1]
    else:
        return ratio


def get_brewer_color_func(freq_df, total_pos, total_neg):
    """ Returns a frequency-aware word coloring function based on a diverging ColorBrewer scheme with 11 classes
            red -> yellow -> green

    Parameters:
    -----------
    freq_df : a DataFrame created with `process_cat` function
        This needs to have at least (pos, neg, ...) columns
    """

    diverging_scheme = [ # red - yellow - green : http://colorbrewer2.org/#type=diverging&scheme=RdYlGn&n=11
      (165,0,38), (215,48,39), (244,109,67), (253,174,97), (254,224,139), (255,255,191), (217,239,139),
      (166,217,106), (102,189,99), (26,152,80), (0,104,55),
    ]
    max_idx = len(diverging_scheme) - 1

    def word_color_mapper(word, font_size, position, orientation, font_path=None, random_state=None):
        """ Function to be called by a wordcloud on each word. This one is aware of the word positive/negative
        frequencies and places the word accordingly in the colour scheme
        """
        pos, neg = freq_df.at[word, 'pos'], freq_df.at[word, 'neg']
        score = score_word(pos, neg, total_pos, total_neg)
        color_idx = int(score * max_idx)

        assert(color_idx >= 0 and color_idx < len(diverging_scheme))
        return 'rgb({:.0f}, {:.0f}, {:.0f})'.format(*diverging_scheme[color_idx])

    return word_color_mapper


def get_cmap_color_func(freq_df, total_pos, total_neg, colormap):
    """ Returns a frequency-aware coloring function based on the given colormap name

    Parameters:
    -----------
    freq_df: a DataFrame created with `process_cat` function
        This needs to have at least (pos, neg, ...) columns
    """
    import matplotlib.pyplot as plt
    colormap = plt.cm.get_cmap(colormap)

    def word_color_mapper(word, font_size, position, orientation, font_path=None, random_state=None):
        """ Function to be called by a wordcloud on each word. This one is aware of the word positive/negative
        frequencies and places the word accordingly based on the colormap
        """
        pos, neg = freq_df.at[word, 'pos'], freq_df.at[word, 'neg']
        score = score_word(pos, neg, total_pos, total_neg)
        r,g,b,a = colormap(score, bytes=True)
        return 'rgb({},{},{})'.format(r,g,b)

    return word_color_mapper


def add_legend(img, cmap_name):
    """ Adds a legend on the image with the given colormap name"""
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    import numpy as np

    # we can 'crop' with a bigger size to get a bigger image in 1 step
    # the legend sits 20% to the right of the current image
    orig_w, orig_h = img.size
    new_img = img.crop((0,0, orig_w + 0.2*orig_w, orig_h))
    new_img.load() # force cropping NOW!

    # set the background of the new region
    draw = ImageDraw.Draw(new_img)
    draw.rectangle(((orig_w,0), (new_img.width,new_img.height)), fill='#FFF')

    legend_h = int(0.8 * orig_h) # only 80% to leave some space for labels
    legend_w = int(0.1 * orig_w) # only 10% to leave some margins

    # sample the colormap to build an image of the legend [from a (legend_h x legend_w) array]
    legend_arry = plt.get_cmap(cmap_name)(np.linspace(0,1,legend_h).repeat(legend_w).reshape(legend_h,legend_w), bytes=True)
    legend_img = Image.fromarray(legend_arry) # the name is actually legend___wait_for_it___arry

    # add it centred in the extra space we created. check it ! :)
    leg_offset = (int(orig_w + 0.05*orig_w), int(0 + 0.1*orig_h))
    new_img.paste(legend_img, leg_offset)

    # add text labels around the legend
    font = ImageFont.truetype('DroidSansMono.ttf', 22)

    # draw text at upper bound; you can use `tuple(legend_arry[0,0,:3])` to use the same one as legend top
    text_offset = (leg_offset[0], leg_offset[1] - 25 * 2) # 25 * 2 = 2 lines and a bit
    draw.text(text_offset, "Mostly\nnegative", (255,255,255), font=font)

    text_offset = (leg_offset[0], leg_offset[1] + legend_h + 6)
    draw.text(text_offset, "Mostly\npositive", (255,255,255), font=font)

    return new_img


def get_cloud_fitter(cat_name, cat_df, wc, check_exists=True):
    """ Gives you a smart function adaptate to the wordcloud and the dataframe which
    can generate `pos | neg | total` wordclouds

    Parameters:
    -----------
    cat_name : name of the category being fit. This is used to find a bit-mask and to
        save the result under the correct name
    cat_df   : the associated DataFrame with review texts and ratings
    wc       : a wordcloud instance cached for the returned function
        Note: if you change make changes to the wordcloud between this function and
        using the result `fitter`, they will reflect as the object is not copied
    check_exists : flag whether to skip the category (or an image in the fitter) if it
        already exists
    """
    from os import path
    from glob import glob
    from scipy.misc import imread
    from PIL import Image

    # skip the costly fit if we have everything for this `cat_name`
    num_existing_files = len(glob(path.join('clouds', cat_name+'*.png')))
    if check_exists and num_existing_files == 3:
        print('Skipping {} altogether'.format(cat_name), flush=True)
        return lambda *args, **kwargs: None # return a dummy function

    # check and load a mask
    mask_path, mask = path.join("masks", cat_name + ".png"), None
    if path.isfile(mask_path):
        mask = imread(mask_path)

        # uncomment the following lines to allow the mask to use the most area available
#         if mask.sum() > np.invert(mask).sum(): # we have more white
#             mask = np.invert(mask)

    # update the mask (with None if it wasn't found)
    wc.mask = mask

    print("processing", cat_name, flush=True)
    freq_df, total_pos, total_neg = process_cat(cat_df, wc)

    # mapping from type to colormap
    cmaps = {'pos' : 'Greens', 'neg' : 'OrRd_r', 'total':'RdYlGn'}

    def fitter(cloud_type='total', save=True, legend=False):
        """ Fits the words in the given type to the preset cloud

        Parameters:
        -----------
        cloud_type : (total | pos | neg)
        """

        # sanity check
        assert(cloud_type in cmaps.keys())

        # again, check for each image and skip if it exists
        img_name = path.join('clouds', '{}_{}.png'.format(cat_name, cloud_type))
        if check_exists and path.isfile(img_name):
            print('Skipping', img_name)
            return

        # tune color_func for this type and generate
        wc.color_func = get_cmap_color_func(freq_df, total_pos, total_neg, cmaps[cloud_type])
        wc.fit_words(freq_df[cloud_type].to_dict())
        img = wc.to_image()

        # keep the background only where needed; This way the results are 'self consistent' and can be used in presentations
        if mask is not None:
            # turn it into image
            mask_img = Image.fromarray(mask[:,:,0])
            img = Image.composite(mask_img, img, mask_img)

        if legend:  # for poster, don't add legend on each file
            img = add_legend(img, cmaps[cloud_type])

        if save:    # useful for dummy run
            print('Saving', img_name, flush=True)
            img.save(img_name)
            img.close()

    return fitter
