import requests
import re
import os
import os.path
import time
import vk_api
from functools import reduce
from math import ceil
from random import randint
from time import sleep


def remove_chars(value, chars_to_remove):
    for c in chars_to_remove:
        value = value.replace(c, '')
    return value


def captcha_handler(captcha_inp):
    captcha_out = input('Enter captcha %s: ' % captcha_inp.get_url())

    return captcha_inp.try_again(captcha_out)


def exception(ex):
    print(ex)
    exit()


def set_up(vk_session, owner_id, root_folder):
    vk = vk_session.get_api()
    values = dict()

    try:
        values['albums'] = vk.photos.getAlbums(owner_id=owner_id)['items']

        if not os.path.exists(root_folder):
            os.makedirs(root_folder)

    except Exception as ex:
        exception(ex)

    special_albums = [{"title": 'wall', "id": 'wall'}, {"title": 'profile', "id": 'profile'}]

    try:
        vk.photos.get(owner_id=owner_id, album_id='saved')
        special_albums = special_albums + [{"title": 'saved', "id": 'saved'}]
    except:
        pass

    values['albums'] = values['albums'] + special_albums

    print('\nall albums:\n' + '\n'.join(['{} - id: {}'.format(album['title'], album['id']) for album in values['albums']]) + '\n')

    values['album_ids'] = [album['id'] for album in values['albums']]
    values['album_names'] = [remove_chars(album['title'], '\/:*?"<>|') for album in values['albums']]
    values['album_paths'] = ['{}{}\\'.format(root_folder, album) for album in values['album_names']]
 
    try:
        for item in values['album_paths']:
            if not os.path.exists(item):
                os.makedirs(item)
    except Exception as ex:
        exception(ex)

    return vk, values


def getPhotos(vk, offset, owner_id, album_id):
    photosSplit = vk.photos.get(
        owner_id=owner_id, 
        offset=offset,
        count=1000, 
        album_id=album_id
    )

    # index == -1 is for largest picture
    return [i['sizes'][-1]['url'] for i in photosSplit['items']]


def save_photo(folder, photos, iterations_range):

    print('\nfolder: {}\n'.format(folder))

    for photo_url in photos:     
        try:
            photo_name = '{}.jpg'.format(time.time()) 
            request = requests.get(photo_url)
            if request.status_code == 200:
                file_path = '{}{}'.format(folder, photo_name)
                try:
                    if os.path.exists(file_path):
                        print('file already exists')
                    else: 
                        with open(file_path, 'wb') as fd:
                            fd.write(request.content)    
                            print('{} : {}'.format(photo_url, 'saved'))
                except Exception as ex:
                    print(ex)
            else:
                print('{} : connection error'.format(photo_url))
        except Exception as ex:
            print(ex)


if __name__ == '__main__':

    username = ''                       #TYPE LOGIN    HERE
    password = ''                       #TYPE PASSWORD HERE
    owner_id = int('')                  #TYPE PAGE  ID HERE
    root_folder = 'C:\\folder_name\\'   #TYPE SAVE DIRECTORY HERE (PARENT FOLDER MUST EXIST)

    vk_session = vk_api.VkApi(
        username,
        password,
        captcha_handler=captcha_handler
    )

    try:
        vk_session.auth()
        vk, settings = set_up(vk_session, owner_id, root_folder)

        for album_id, folder in zip(settings['album_ids'], settings['album_paths']):

            count = vk.photos.get(owner_id=owner_id, album_id=album_id)['count']
            iterations = ceil(int(count) / 1000)  
            iterations_range = range(0, iterations)

            photos = [getPhotos(vk, i * 1000, owner_id, album_id)
                      for i in iterations_range]

            photos = reduce(lambda d, el: d.extend(el) or d, photos, [])

            save_photo(folder, photos, iterations_range)

    except Exception as ex:
        exception(ex)