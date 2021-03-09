from ytmusicapi import YTMusic
from difflib import SequenceMatcher


def main():

  oldAccount = YTMusic('old_account.json')
  newAccount = YTMusic('new_account.json')

  playlists = oldAccount.get_library_playlists()
  playlistName = "Traveling Home"

  tracks = None
  found = False

  for playlist in playlists:
    if playlist['title'] == playlistName:
      oldPlaylist = oldAccount.get_playlist(playlistId=playlist['playlistId'], limit=3000)
      tracks = oldPlaylist['tracks']
      found = True

  if (found):

    songs = []
    failedsongs = []

    i = 0

    for track in tracks:
      i+=1
      artists = track['artists']
      if artists:
        for artist in artists:
          songs.append(artist['name'] + " - " + track['title'])
      else:
        songs.append(track['title'])
    print("playlist song count: " + str(i))

    playlistId = newAccount.create_playlist(playlistName, description=playlistName)

    for song in songs:
      print("Processing Song: " + song)
      search_results_songs = newAccount.search(song, filter="songs")
      search_results_videos = newAccount.search(song, filter="videos")

      result = determineVideoId(song, search_results_songs, search_results_videos)

      if result and result['videoId']:
        print(getSongName(result))
        response = newAccount.add_playlist_items(playlistId, [result['videoId']])
        print(response)
      else:
        print("No Song found")
        failedsongs.append(song)
      print("--------------------------------------------")
    print("Songs which where not transferred")
    print(failedsongs)

def determineVideoId(song, search_results_songs, search_results_videos):
  result = None

  if search_results_songs and not search_results_videos:
    result = search_results_songs[0]
  elif search_results_videos and not search_results_songs:
    result = search_results_videos[0]
  elif search_results_videos and search_results_songs:
    result = similar(song, search_results_songs[0], search_results_videos[0])
  return result

def similar(searchString, resultA, resultB):
  if SequenceMatcher(None, searchString, getSongName(resultA)).ratio() > SequenceMatcher(None, searchString, getSongName(resultB)).ratio():
    return resultA
  else:
    return resultB

def getSongName(result):
  if result['artists']:
    return result['artists'][0]['name'] + "-" + result['title']
  else:
    return result['title']

if __name__ == '__main__':
  main()