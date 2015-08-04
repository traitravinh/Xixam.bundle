# __author__ = 'traitravinh'
import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
################################## XIXAM #########################################
NAME = "Xixam"
BASE_URL = "http://phim.xixam.com"
M_BASE_URL='http://phim.xixam.com/m'
SEARH_URL = 'http://phim.xixam.com/tim-kiem/?tk=%s'
DEFAULT_ICO = 'icon-default.png'
SEARCH_ICO = 'icon-search.png'
NEXT_ICO = 'icon-next.png'
##### REGEX #####

# ###################################################################################################

def Start():
    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR

    DirectoryObject.thumb = R(DEFAULT_ICO)

    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['X-Requested-With'] = 'XMLHttpRequest'
####################################################################################################

@handler('/video/xixam', NAME)
def MainMenu():
    oc = ObjectContainer()
    oc.add(InputDirectoryObject(
        key=Callback(Search),
        title='SEARCH'
    ))
    try:
        link = HTTP.Request(BASE_URL,cacheTime=3600).content
        soup = BeautifulSoup(link)
        ul_sf_menu = soup('ul', {'class':'sf-menu'})
        li = BeautifulSoup(str(ul_sf_menu[0]))('li')
        for l in li:
            ltitle = BeautifulSoup(str(l))('a')[0].contents[0]
            llink = BeautifulSoup(str(l))('a')[0]['href']
            if ltitle!=' ' and llink!='javascript:;':
                oc.add(DirectoryObject(
                    key=Callback(Category, title=ltitle, catelink=BASE_URL+llink),
                    title=ltitle,
                    thumb=R(DEFAULT_ICO)
                ))

    except Exception, ex:
        Log("******** Error retrieving and processing latest version information. Exception is:\n" + str(ex))

    return oc
####################################################################################################

@route('/video/xixam/search')
def Search(query=None):
    if query is not None:
        url = SEARH_URL % (String.Quote(query, usePlus=True))
        return Category(query,url)

@route('/video/xixam/category')
def Category(title, catelink):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(catelink,cacheTime=3600).content
    soup = BeautifulSoup(link.decode('utf-8'))

    div_block = soup('div',{'class':'BlockProduct2 '})#space after BlockProduct2
    for div in div_block:
        div_title = BeautifulSoup(str(div))('a')[1].contents[0]
        div_link = BeautifulSoup(str(div))('a')[0]['href']
        div_img = BeautifulSoup(str(div))('img')[0]['src']
        if div_img.find('http://') == -1:
            div_img = BASE_URL+div_img
        oc.add(DirectoryObject(
            key=Callback(Server, title=div_title, svlink=BASE_URL+div_link, svthumb=div_img, inum=None),
            title=div_title,
            thumb=div_img
        ))
    try:
        div_fr_page_links = soup('div',{'class':'fr_page_links'})
        pages = BeautifulSoup(str(div_fr_page_links[0]))('a')
        for p in pages:
            ptitle = BeautifulSoup(str(p))('a')[0].contents[0]
            plink = BeautifulSoup(str(p))('a')[0]['href']
            oc.add(DirectoryObject(
                key=Callback(Category, title=ptitle, catelink=BASE_URL+plink),
                title=ptitle,
                thumb=R(NEXT_ICO)
            ))
    except:pass

    return oc

####################################################################################################
@route('/video/xixam/server')
def Server(title, svlink, svthumb, inum):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(overview(svlink),cacheTime=3600).content
    soup = BeautifulSoup(link)
    div_serverlist = soup('div',{'class':'serverlist'})
    if inum is None:
        for i in range(0,len(div_serverlist)):
            svtitle = BeautifulSoup(str(div_serverlist[i]))('div',{'class':'serverlist'})[0].next.contents[0]
            svindex = i
            oc.add(DirectoryObject(
                key=Callback(Server, title=svtitle, svlink=svlink, svthumb=svthumb, inum=svindex),
                title=svtitle,
                thumb=svthumb
            ))
    else:
        episodes = BeautifulSoup(str(div_serverlist[int(inum)]))('a')
        Log(episodes)
        for e in episodes:
            etitle = BeautifulSoup(str(e))('a')[0].contents[0]
            try:
                elink =''.join([M_BASE_URL,'/',BeautifulSoup(str(e))('a')[0]['href']])
            except:pass

            oc.add(createMediaObject(
                url=elink,
                title=etitle,
                thumb=svthumb,
                rating_key=etitle
            ))

    return oc

@route('/video/xixam/createMediaObject')
def createMediaObject(url, title,thumb,rating_key,include_container=False,includeRelatedCount=None,includeRelated=None,includeExtras=None):
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2
    track_object = EpisodeObject(
        key = Callback(
            createMediaObject,
            url=url,
            title=title,
            thumb=thumb,
            rating_key=rating_key,
            include_container=True
        ),
        title = title,
        thumb=thumb,
        rating_key=rating_key,
        items = [
            MediaObject(
                parts=[
                    PartObject(key=Callback(PlayVideo, url=url))
                ],
                container = container,
                video_resolution = '720',
                video_codec = video_codec,
                audio_codec = audio_codec,
                audio_channels = audio_channels,
                optimized_for_streaming = True
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object


@indirect
def PlayVideo(url):
    # return IndirectResponse(VideoClipObject, key=url)
    url = videolinks(url)
    if str(url).find('youtube')!=-1:
        oc = ObjectContainer(title2='Youtube Video')
        oc.add(VideoClipObject(
            url=url,
            title='Youtube video',
            thumb=R(DEFAULT_ICO)
        ))
        return oc
    else:
        return IndirectResponse(VideoClipObject, key=url)


def overview(url):
    link = HTTP.Request(url,cacheTime=3600).content
    soup = BeautifulSoup(link)
    div_overview = soup('div',{'class':'overview'})
    p_style_10px = BeautifulSoup(str(div_overview[0]))('p',{'style':'padding-top:10px'})
    return M_BASE_URL+BeautifulSoup(str(p_style_10px[0]))('a')[0]['href']

def videolinks(url):
    link = HTTP.Request(url,cacheTime=3600).content
    soup = BeautifulSoup(link)
    if link.find('http://www.youtube.com/embed/')!=-1:
        video = soup('iframe')[1]['src']
    else:
        video = BeautifulSoup(str(soup('video')[0]))('source')[0]['src']
    return video

####################################################################################################
