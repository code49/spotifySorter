import json

# Load tracks from playlist_tracks.json
with open("playlist_tracks.json", "r") as f:
    data = json.load(f)

tracks = data["tracks"]
print(f"Total tracks in file: {len(tracks)}")

# Let's map each track to a playlist category
# We will use the track ID as the key to avoid naming collision/mismatches

# Category definitions
categories = {
    "hard-rock": {
        "description": "[ai sorted] High Energy Hard Rock and Heavy Metal. Powerful, raw, and high-voltage rock anthems.",
        "ids": []
    },
    "classic-rock": {
        "description": "[ai sorted] Mid-to-High Energy Classic Rock. Timeless stadium rock, nostalgic road-trip anthems, and retro rock favorites.",
        "ids": []
    },
    "dance-pop": {
        "description": "[ai sorted] High Energy Modern Dance-Pop and Electro. Catchy, upbeat pop hits and club-ready tracks.",
        "ids": []
    },
    "chill-pop": {
        "description": "[ai sorted] Low-to-Mid Energy Chill Pop and Mellow R&B. Smooth, relaxed melodies and cozy bedroom pop vibes.",
        "ids": []
    },
    "indie-pop": {
        "description": "[ai sorted] Mid-to-High Energy Indie Pop and Alt Rock. Punchy alternative guitars, indie anthems, and energetic modern bands.",
        "ids": []
    },
    "retro-pop": {
        "description": "[ai sorted] Mid-to-High Energy Retro Pop, Disco and Funk. Feel-good classic pop, dancefloor grooves, and soul from the 70s and 80s.",
        "ids": []
    },
    "jazz-acoustic": {
        "description": "[ai sorted] Low Energy Acoustic, Jazz, and Folk. Intimate vocals, jazz standards, and soothing acoustic arrangements.",
        "ids": []
    },
    "hip-hop": {
        "description": "[ai sorted] Mid-to-High Energy Hip-Hop and Rap. Punchy beats, bold rap flows, and modern urban rhythms.",
        "ids": []
    }
}

# Mapping rules
# Let's make an explicit mapping for every single ID
mapping = {
    # hard-rock
    "7snQQk1zcKl8gZ92AnueZW": "hard-rock", # Sweet Child O' Mine
    "0G21yYKMZoHa30cYVi1iA8": "hard-rock", # Welcome To The Jungle
    "2zYzyRzz6pRmhPzyfMEC8s": "hard-rock", # Highway to Hell
    "57bgtoPSgt236HzfBOd8kj": "hard-rock", # Thunderstruck
    "08mG3Y1vljYA6bvDt4Wqkj": "hard-rock", # Back In Black
    "7LRMbd3LEoV5wZJvXT1Lwb": "hard-rock", # T.N.T.
    "7ACxUo21jtTHzy7ZEV56vU": "hard-rock", # Crazy Train
    "6nTiIhLmQ3FWhvrGafw2zj": "hard-rock", # American Idiot
    "6L89mwZXSOwYl76YXfX13s": "hard-rock", # Basket Case
    "7oJ3Nb3LIY1ond1fHF3xio": "hard-rock", # MAMMAMIA - Maneskin
    "63T7DJ1AFDD6Bn8VzG6JE8": "hard-rock", # Paint It, Black - Stones
    "2HHtWyy5CgaQbC7XSoOb0e": "hard-rock", # Eye of the Tiger - Survivor (heavy energy, can be hard or classic rock)
    "7N3PAbqfTjSEU1edb2tY8j": "hard-rock", # Jump - Van Halen
    
    # classic-rock
    "7EHmKkyAr6MZv5Y2FdZbXw": "classic-rock", # Lights - Journey
    "4bHsxqR3GMrXTxEPLuK5ue": "classic-rock", # Don't Stop Believin' - Journey
    "37ZJ0p5Jm13JPevGcx4SkF": "classic-rock", # Livin' On A Prayer - Bon Jovi
    "7e89621JPkKaeDSTQ3avtg": "classic-rock", # Sweet Home Alabama - Lynyrd Skynyrd
    "40riOy7x9W7GXjyGp4pjAv": "classic-rock", # Hotel California - Eagles
    "2olVm1lHicpveMAo4AUDRB": "classic-rock", # The Power Of Love - Huey Lewis
    "39shmbIHICJ2Wxnk1fPSdz": "classic-rock", # Should I Stay or Should I Go - The Clash
    "0pQskrTITgmCMyr85tb9qq": "classic-rock", # Starman - David Bowie
    "0rmGAIH9LNJewFw7nKzZnc": "classic-rock", # You Give Love A Bad Name - Bon Jovi
    "6iX1f3r7oUJnMbGgQ2gx1j": "classic-rock", # 867-5309 / Jenny - Tommy Tutone
    "3Cx4yrFaX8CeHwBMReOWXI": "classic-rock", # We Didn't Start the Fire - Billy Joel
    "1fDsrQ23eTAVFElUMaf38X": "classic-rock", # American Pie - Don McLean
    "0GONea6G2XdnHWjNZd6zt3": "classic-rock", # Summer Of '69 - Bryan Adams
    "6OnfBiiSc9RGKiBKKtZXgQ": "classic-rock", # We Built This City - Starship
    "2Fs18NaCDuluPG1DHGw1XG": "classic-rock", # Life is a Highway - Rascal Flatts
    "5nDSJO4909uNzMcZH3CggS": "classic-rock", # Hard to Say I'm Sorry - Chicago
    
    # dance-pop
    "7rglLriMNBPAyuJOMGwi39": "dance-pop", # Cold Heart
    "2ekn2ttSfGqwhhate0LSR0": "dance-pop", # New Rules - Dua Lipa
    "76hfruVvmfQbw0eYn1nmeC": "dance-pop", # Cake By The Ocean
    "6ocbgoVGwYJhOv1GgI9NsF": "dance-pop", # 7 rings
    "32OlwWuMpZ6b0aN2RZOeMS": "dance-pop", # Uptown Funk
    "6KOEK6SeCEZOQkLj5M1PxH": "dance-pop", # California Gurls
    "60nZcImufyMA1MKQY3dcCH": "dance-pop", # Happy - Pharrell
    "6b8Be6ljOzmkOmFslEb23P": "dance-pop", # 24K Magic - Bruno Mars
    "4Y7XAxTANhu3lmnLAzhWJW": "dance-pop", # Fireball - Pitbull
    "0VjIjW4GlUZAMYd2vXMi3b": "dance-pop", # Blinding Lights - The Weeknd
    "22oEJW6r2rMb9z4IntfyEa": "dance-pop", # Hey Look Ma - Panic!
    "0IkKz2J93C94Ei4BvDop7P": "dance-pop", # Party Rock Anthem - LMFAO
    "1kPpge9JDLpcj15qgrPbYX": "dance-pop", # Good Time - Owl City / Carly Rae
    "5ZkAx8zjLiSs1nMmBwJoZS": "dance-pop", # When Can I See You Again? - Owl City
    "7EQGXaVSyEDsCWKmUcfpLk": "dance-pop", # Die Young - Kesha
    "2qT1uLXPVPzGgFOx4jtEuo": "dance-pop", # no tears left to cry - Ariana Grande
    "19RybK6XDbAVpcdxSbZL1o": "dance-pop", # Apple - Charli xcx
    "4w2GLmK2wnioVnb5CPQeex": "dance-pop", # 360 - Charli xcx
    "3avYqdwHKEq8beXbeWCKqJ": "dance-pop", # Last Friday Night - Katy Perry
    "6MAdEUilV2p9RQUqE5bMAK": "dance-pop", # Domino - Jessie J
    "5hyq3LBlCfjRQAFkdQwe8o": "dance-pop", # Vroom Vroom - Charli xcx
    "3cZajhyr8LmtPfHZ9296tj": "dance-pop", # No Broke Boys - Disco Lines
    "2yWlGEgEfPot0lv3OAjuG3": "dance-pop", # Just Keep Watching - Tate McRae
    "7vS3Y0IKjde7Xg85LWIEdP": "dance-pop", # Problem - Ariana Grande
    "09IStsImFySgyp0pIQdqAc": "dance-pop", # The Middle - Zedd
    "1rIKgCH4H52lrvDcz50hS8": "dance-pop", # Lush Life - Zara Larsson
    "1kUyOJb3fzUo8r0OCz5SQk": "dance-pop", # Mantra - JENNIE
    "12KUFSHFgT0XCoiSlvdQi4": "dance-pop", # Break Free - Ariana Grande
    "6QFCMUUq1T2Vf5sFUXcuQ7": "dance-pop", # Beauty And A Beat - Justin Bieber
    "0am001WwFBVGDGLwRh3ixi": "dance-pop", # Rather Be - Clean Bandit
    "4E5P1XyAFtrjpiIxkydly4": "dance-pop", # Replay - Iyaz
    "2H1047e0oMSj10dgp7p2VG": "dance-pop", # I Gotta Feeling - BEP
    "2hloaUoRonYssMuqLCBLTX": "dance-pop", # bloodline - Ariana Grande
    "4NczzeHBQPPDO0B9AAmB8d": "dance-pop", # Assumptions - Sam Gellaitry
    "0Mh4zlDsN7s0YMbsas12et": "dance-pop", # Join Us for a Bite - JT Music
    
    # indie-pop
    "3dPQuX8Gs42Y7b454ybpMR": "indie-pop", # Seven Nation Army
    "27L8sESb3KR79asDUBu8nW": "indie-pop", # Stacy's Mom
    "4kbj5MwxO1bq9wjT5g9HaA": "indie-pop", # Shut Up and Dance
    "6QgjcU0zLnzq5OrUoSZ3OK": "indie-pop", # Feel It Still
    "2tpWsVSb9UEmDRxAl1zhX1": "indie-pop", # Counting Stars
    "1zB4vmk8tFRmM9UULNzbLB": "indie-pop", # Thunder
    "2iUXsYOEPhVqEBwsqP70rE": "indie-pop", # Youngblood
    "3NxWJWftvkstyxvb1pZlFo": "indie-pop", # Teeth
    "6KuHjfXHkfnIjdmcIvt9r0": "indie-pop", # On Top Of The World
    "1rqqCSm0Qe4I9rUvWncaom": "indie-pop", # High Hopes
    "3Te8uLyit6X3ncNW8Fp3K2": "indie-pop", # Immortals - Fall Out Boy
    "2wCYxNcQwopc6VgtK1ydWM": "indie-pop", # Learn to Fly - Foo Fighters
    "0d28khcov6AiegSCpG5TuT": "indie-pop", # Feel Good Inc. - Gorillaz
    "6QewNVIDKdSl8Y3ycuHIei": "indie-pop", # Even Flow - Pearl Jam
    "04aAxqtGp5pv12UXAg4pkq": "indie-pop", # Centuries - Fall Out Boy
    "3mwvKOyMmG77zZRunnxp9E": "indie-pop", # Buddy Holly - Weezer
    "2MLHyLy5z5l5YRp7momlgw": "indie-pop", # Island In The Sun - Weezer
    "6VoIBz0VhCyz7OdEoRYDiA": "indie-pop", # Say It Ain't So - Weezer
    "1yKu2MhpwzDXXH2tzG6xoa": "indie-pop", # Beverly Hills - Weezer
    "0JJP0IS4w0fJx01EcrfkDe": "indie-pop", # Dear Maria - All Time Low
    "003vvx7Niy0yvhvHt4a68B": "indie-pop", # Mr. Brightside - The Killers
    "3SXXFIZel1VQQ4ENiqozxi": "indie-pop", # Still into You - Paramore
    "20I8RduZC2PWMWTDCZuuAN": "indie-pop", # Take Me Out - Franz Ferdinand
    "3ZOEytgrvLwQaqXreDs2Jx": "indie-pop", # Can't Stop - RHCP
    "1170VohRSx6GwE6QDCHPPH": "indie-pop", # Kilby Girl - Backseat Lovers
    "1gugDOSMREb34Xo0c1PlxM": "indie-pop", # She Looks So Perfect - 5SOS
    "6t6oULCRS6hnI7rm0h5gwl": "indie-pop", # Some Nights - fun.
    "2iUmqdfGZcHIhS3b9E9EWq": "indie-pop", # Everybody Talks - Neon Trees
    "751srcHf5tUqcEa9pRCQwP": "indie-pop", # Tek It - Cafuné
    "5Hroj5K7vLpIG4FNCRIjbP": "indie-pop", # Best Day Of My Life
    "5JVbvCHX10U2pLa5DEqGav": "indie-pop", # Safe and Sound
    # chill-pop
    "4LRPiXqCikLlN15c3yImP7": "chill-pop", # As It Was
    "7BKLCZ1jbUBVqRi2FVlTVw": "chill-pop", # Closer
    "7BqBn9nzAq8spo5e7cZ0dJ": "chill-pop", # Just the Way You Are
    "0KKkJNfGyhkQ5aFogxQAPU": "chill-pop", # That's What I Like
    "6PCUP3dWmTjcTtXY02oFdT": "chill-pop", # Castle on the Hill
    "0afhq8XCExXpqazXczTSve": "chill-pop", # Galway Girl
    "7JJmb5XwzOO8jgpou264Ml": "chill-pop", # There's Nothing Holdin' Me Back
    "3w3y8KPTfNeOKPiqUTakBh": "chill-pop", # Locked out of Heaven
    "4cktbXiXOapiLBMprHFErI": "chill-pop", # Memories
    "3DamFFqW32WihKkTVlwTYQ": "chill-pop", # Fireflies
    "0vCTQcxSGAgjHaiAsIANKn": "chill-pop", # Vanilla Twilight
    "1oew3nFNY3vMacJAsvry0S": "chill-pop", # Me And My Broken Heart
    "6FE2iI43OZnszFLuLtvvmg": "chill-pop", # Classic - MKTO
    "0d2iYfpKoM0QCKvcLCkBao": "chill-pop", # Eastside
    "3KkXRkHbMCARz0aVfEt68P": "chill-pop", # Sunflower
    "3VawzwYnB6Fk637uqueuZq": "chill-pop", # everyday - Chevy
    "3HopXEwE96WWXPP4OK78wW": "chill-pop", # I Know a Place - Chevy
    "7gA5OQWsvAY7HhazroFuwI": "chill-pop", # Save Me, San Francisco
    "0fK7ie6XwGxQTIkpFoWkd1": "chill-pop", # like JENNIE
    "3wWlIamAbDeN1sw7MUKsBG": "chill-pop", # Fallin' Twice - Chevy
    "53U4TXdEBFtRe9VS2U43FQ": "chill-pop", # Dial 143 - jomm
    "3FYIfyziD8T4CvxnpLePb4": "chill-pop", # starsmitten - LilyPichu
    "0qOnSQQF0yzuPWsXrQ9paz": "chill-pop", # Stereo Hearts
    "6ECp64rv50XVz93WvxXMGF": "chill-pop", # This Love
    "161DnLWsx1i3u1JT05lzqU": "chill-pop", # Talking to the Moon
    "4P0osvTXoSYZZC2n8IFH3c": "chill-pop", # Payphone
    "6f68Ac5tt5BQOpwr0BV9oN": "chill-pop", # I Just Might
    "79esEXlqqmq0GPz0xQSZTV": "chill-pop", # Lost In Japan
    "68HocO7fx9z0MgDU0ZPHro": "chill-pop", # Every Summertime
    "4cluDES4hQEUhmXj6TXkSo": "chill-pop", # What Makes You Beautiful
    "6AQbmUe0Qwf5PZnt4HmTXv": "chill-pop", # Boy's a liar Pt. 2
    "5odlY52u43F5BjByhxg7wg": "chill-pop", # golden hour
    "76oCvJj6LRoed2754GybpH": "chill-pop", # mosi mosi?
    "5yvVYFDUpbnjcnRBgjwTzM": "chill-pop", # Dracula - JENNIE Remix
    "4XNrMwGx1SqP01sqkGTDmo": "chill-pop", # One More Night
    "2PWTZV5znjLtZC5T1EVJvL": "chill-pop", # this is what falling in love feels like
    "2RkZ5LkEzeHGRsmDqKwmaJ": "chill-pop", # Ordinary - Alex Warren
    "0Ryd8975WihbObpp5cPW1t": "chill-pop", # boyfriend - Ariana
    "2Bs4jQEGMycglOfWPBqrVG": "chill-pop", # Steal My Girl
    "21B4gaTWnTkuSh77iWEXdS": "chill-pop", # Juno - Sabrina Carpenter
    "1jEBSDN5vYViJQr78W7jr2": "chill-pop", # Light Switch - Charlie Puth
    "2JzZzZUQj3Qff7wapcbKjc": "chill-pop", # See You Again - Charlie Puth/Wiz
    "4oTn7ylKtjeMYwxatEVFAt": "chill-pop", # Loser - Charlie Puth
    "0wPKDeY4fZXT6k9bzV0kx0": "chill-pop", # That's Hilarious - Charlie Puth
    "793tMto9guBs0X6c44R5mH": "chill-pop", # Washed Up - Charlie Puth
    "4HlFJV71xXKIGcU3kRyttv": "chill-pop", # Hey, Soul Sister
    "4e1tzRx6ILKkLYvTQzOg55": "chill-pop", # Ocean - Jeena
    "1PtlEQB07a2O1ZpcTGpGWx": "chill-pop", # Broken House - Jeena
    "6RmUQLMhSYchblq4hu5YYl": "chill-pop", # TV Families - Jeena
    "1h9bWGOMsk93eongcnuNLr": "chill-pop", # Flourish - Jeena
    "6o234fdT6LUyELoBfBOlEv": "chill-pop", # The Train - Jeena
    "46E8BIFdHDpNQ97R4d9WTS": "chill-pop", # Forgetting - Jeena
    "2JVZSUwPWzfBdgkdy3ZHet": "chill-pop", # Still Alive - Aperture
    "1uS5Ca356z4zQ7NfaqVAac": "chill-pop", # Want You Gone - Aperture
    "7qiZfU4dY1lWllzX7mPBI3": "chill-pop", # Shape of You - Ed Sheeran
    
    # retro-pop
    "2WfaOiMkCvy7F5fcp2zZ8L": "retro-pop", # Take on Me
    "22NN4BS1AlqVbyKIWExgON": "retro-pop", # Mamma Mia
    "0GjEhVFGZW8afUYGChu3Rr": "retro-pop", # Dancing Queen
    "3Dy4REq8O09IlgiwuHQ3sk": "retro-pop", # Waterloo
    "34x6hEJgGAOQvmlMql5Ige": "retro-pop", # Danger Zone
    "5mQYBoGU3BOAqiFq54b51i": "retro-pop", # Playing with the Boys
    "0ikz6tENMONtK6qGkOrU3c": "retro-pop", # Wake Me Up Before You Go-Go
    "6W2VbtvMrDXm5vYeB7amkO": "retro-pop", # Footloose
    "4YOJFyjqh8eAcbKFfv88mV": "retro-pop", # Y.M.C.A.
    "62AuGbAkt8Ox2IrFFb8GKV": "retro-pop", # Sweet Caroline
    "2Nz6aF1umHh5Et6I5H581L": "retro-pop", # Hooked On A Feeling
    "7xe3EQCvXnx6Q0zs41Y65n": "retro-pop", # Great Balls of Fire
    "2QfiRTz5Yc8DdShCxG1tB2": "retro-pop", # Johnny B. Goode
    "1jDJFeK9x3OZboIAHsY9k2": "retro-pop", # I'm Still Standing
    "5ZBeML7Lf3FMEVviTyvi8l": "retro-pop", # Twist And Shout
    "2LlQb7Uoj1kKyGhlkBf9aC": "retro-pop", # Thriller
    "67hbP9PFQZrb4XZc3TzB0s": "retro-pop", # Rasputin
    "7J1uxwnxfQLu4APicE5Rnj": "retro-pop", # Billie Jean
    "1mCsF9Tw4AkIZOjvZbZZdT": "retro-pop", # Break My Stride
    "1TfqLAPs4K3s2rJMoCokcS": "retro-pop", # Sweet Dreams
    "0KQh7AuuZvpTKWhcJa8Pbr": "retro-pop", # Funkytown
    "1h2xVEoJORqrg71HocgqXd": "retro-pop", # Superstition
    "19kHhX6f6EfLU7rcO3RqjO": "retro-pop", # Back On 74
    "4RvWPyQ5RL0ao9LPZeSouE": "retro-pop", # Everybody Wants To Rule The World
    "3kXoKlD84c6OmIcOLfrfEs": "retro-pop", # September
    "2RlgNHKcydI9sayD2Df2xp": "retro-pop", # Mr. Blue Sky
    "4o6BgsqLIBViaGVbx5rbRk": "retro-pop", # You Make My Dreams
    "0UAEKR6MERtRUStQcSEdsH": "retro-pop", # Everybody Wants to Rule the World - Lettuce
    "5LxvwujISqiB8vpRYv887S": "retro-pop", # I Want You Back
    "53pZ8y3yMYUNpclGwIufu0": "retro-pop", # Conga
    "3Fzlg5r1IjhLk2qRw667od": "retro-pop", # Dancing in the Moonlight
    "5FMXrphygZ4z3gVDHGWxgl": "retro-pop", # Copacabana
    "6D8kc7RO0rqBLSo2YPflJ5": "retro-pop", # ABC
    "74sUbOF9Zm8LdGUJjxleTl": "retro-pop", # The Saga Begins - Weird Al
    
    # jazz-acoustic
    "3H8Sn0mYsZMPPlMCbebOJ5": "jazz-acoustic", # Danke Schoen
    "43iIQbw5hx986dUEZbr3eN": "jazz-acoustic", # From The Start
    "4KGGeE7RJsgLNZmnxGFlOj": "jazz-acoustic", # Falling Behind
    "6cx5CvFhqN19efStehJqoW": "jazz-acoustic", # Valentine
    "4nwjvcUjV7cexhwA40Bh5i": "jazz-acoustic", # Lover Girl
    "1CFDAKbWftUywLu6YjI9Kv": "jazz-acoustic", # Linus And Lucy
    "3REwKZrXTWHQ01jEaYMVmz": "jazz-acoustic", # Thanksgiving Theme
    "0smzrlYiBiecxfG8p5QDcQ": "jazz-acoustic", # Please, Please, Please Let Me Get What I Want
    
    # hip-hop
    "0CAfXk7DXMnon4gLudAp7J": "hip-hop", # Low
    "38T0tPVZHcPZyhtOcCP7pF": "hip-hop", # STAR WALKIN'
    "1rfofaqEpACxVEHIZBJe6W": "hip-hop", # Havana (Pop-rap crossover, fits best here or dance-pop)
    "0aB0v4027ukVziUGwVGYpG": "hip-hop", # tv off
    "51Fjme0JiitpyXKuyQiCDo": "hip-hop", # Lalala
    "1golLrmqyxDWedF7YUHCOD": "hip-hop", # edamame
    "6CjtS2JZH9RkDz5UVInsa9": "hip-hop", # Thrift Shop
    "22skzmqfdWrjJylampe0kt": "hip-hop", # Can't Hold Us
    "12J1ilos4UeQY2tpRncoxx": "hip-hop", # Night Train
    "4meLZnspakhlEFkjbaW3KL": "hip-hop", # I'm From the Bay
    "2dKkVF2m160z0RNDN2dddc": "hip-hop", # NISSAN ALTIMA
    "1XXimziG1uhM0eDNCZCrUl": "hip-hop", # Up - Cardi B
    "5fZJQrFKWQLb7FpJXZ1g7K": "hip-hop", # A Bar Song
    "7IezwtVIJIPC36LpKMR9d7": "hip-hop", # Violet
    "2wAJTrFhCnQyNSD3oUgTZO": "hip-hop", # Work Out
    "3MgZMXtodXhGzKtdwVCU9y": "hip-hop", # BOY IN RED
    "55lijDD6OAjLFFUHU9tcDm": "hip-hop", # WHERE IS MY HUSBAND! - RAYE (Spoken/Rap/Hip-Hop/Soul)
}

# Let's populate the categories
for track in tracks:
    tid = track["id"]
    if tid not in mapping:
        print(f"Warning: Track {track['name']} (ID: {tid}) by {track['artists']} not in mapping!")
    else:
        cat_name = mapping[tid]
        categories[cat_name]["ids"].append(tid)

# Check if any tracks were missed or extra
all_mapped_ids = list(mapping.keys())
print(f"Total mapped IDs: {len(all_mapped_ids)}")

out_playlists = []
for name, info in categories.items():
    out_playlists.append({
        "name": name,
        "description": info["description"],
        "track_ids": info["ids"]
    })

output_json = {
    "playlists": out_playlists
}

# Verify sum of tracks matches total_tracks
total_sorted = sum(len(p["track_ids"]) for p in out_playlists)
print(f"Total sorted tracks: {total_sorted}")

with open("sorted_playlists.json", "w") as f:
    json.dump(output_json, f, indent=2)
