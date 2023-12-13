from loguru import logger
logger.remove()
def filter_function(record):
    return verbose
logger.add("kerchunking_{time}.log", filter=filter_function)#, compression="tar.gz")
from pathlib import Path
import kerchunk
import fsspec
import ujson
from kerchunk.hdf import SingleHdf5ToZarr
# from rich import print
import hashlib


def generate_file_md5(file_path):
    if not file_path.exists():
        # logger.debug(f"File {file_path} does not exist!")
        # print(f"File {file_path} does not exist!")
        return None
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
        
        if not file_content:
            # logger.debug(f"File {file_path} is empty!")
            # print(f"File {file_path} is empty!")
            return None

        hash_value = hashlib.md5(file_content).hexdigest()
        # logger.debug(f'Hash for {file_path}: {hash_value}')
        # print(f'Hash for {file_path}: {hash_value}')
        return hash_value


def create_single_reference(
    file_path: Path,
    output_directory: Path,
    verbose: int = 0
):
    """ """
    filename = file_path.stem
    output_file = f"{output_directory}/{filename}.json"
    hash_file = f"{output_directory}/{filename}.json.hash"
    generated_hash = generate_file_md5(file_path)
    local_fs = fsspec.filesystem('file')
    if local_fs.exists(output_file) and local_fs.exists(hash_file):
        logger.debug(f'Found a reference file \'{output_file}\' and a hash \'{hash_file}\'')
        with local_fs.open(hash_file, 'r') as hf:
            existing_hash = hf.read().strip()
        
        if existing_hash == generated_hash:
            pass
    else:
        logger.debug(f'Creating reference file \'{output_file}\' with hash \'{generated_hash}\'')
        file_url = f"file://{file_path}"
        with fsspec.open(file_url, mode='rb') as input_file:
            h5chunks = SingleHdf5ToZarr(input_file, file_url, inline_threshold=0)
            json = ujson.dumps(h5chunks.translate()).encode()
            with local_fs.open(output_file, 'wb') as f:
                f.write(json)
            with local_fs.open(hash_file, 'w') as hf:
                hf.write(generated_hash)


if __name__ == "__main__":
    app()
