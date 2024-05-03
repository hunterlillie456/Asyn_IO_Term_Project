import os
import sys
import asyncio

IP = '127.0.0.1'  # default IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_info(data: bytes) -> (str, int):
    return data[8:].decode(), int.from_bytes(data[:8], byteorder='big')


async def upload_file(reader: asyncio.StreamReader, file_name: str, file_size: int):
    # create a new file to store the received data
    print('Uploading File...')
    file_name += '.temp'
    # please do not change the above line!
    with open(file_name, 'wb') as file:
        retrieved_size = 0
        try:
            while retrieved_size < file_size:
                chunk = await reader.read(BUFFER_SIZE)

                retrieved_size += len(chunk)

                file.write(chunk)

        except OSError as oe:
            print(oe)
            os.remove(file_name)


async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        await asyncio.sleep(10)
        print('Starting Task: async handler()')
        message = await reader.read(BUFFER_SIZE)
        # expecting an 8-byte byte string for file size followed by file name

        file_name, file_size = get_file_info(message)
        print(f'A file was received: {file_name} with size = {file_size}')
        await asyncio.sleep(3)

        writer.write(b'go ahead')

        upload_file(file_name, file_size)

        await writer.drain()
        print('Finished Task: async handler()')

    except Exception as e:
        print(e)
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handler, IP, PORT)
    for i in range(len(server.sockets)):
        addr = server.sockets[i].getsockname()
        print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

    server.close()


if __name__ == '__main__':
    # get IP address from cmd line
    if len(sys.argv) == 2:
        IP = sys.argv[1]  # IP from cmdline argument

    asyncio.run(main())
