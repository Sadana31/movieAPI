import os
import urllib.request

FILES = {
    "cosine_sim.pkl": "https://github.com/Sadana31/movieAPI/releases/download/v1/cosine_sim.pkl",
    "indices.pkl": "https://github.com/Sadana31/movieAPI/releases/download/v1/indices.pkl",
    "movies_df.pkl": "https://github.com/Sadana31/movieAPI/releases/download/v1/movies_df.pkl",
}

def download(url, filename):
    if os.path.exists(filename):
        print(f"✅ {filename} already exists, skipping.")
        return
    print(f"⬇️ Downloading {filename} ...")
    urllib.request.urlretrieve(url, filename)
    print(f"✅ Downloaded {filename}")

if __name__ == "__main__":
    for fname, url in FILES.items():
        download(url, fname)

