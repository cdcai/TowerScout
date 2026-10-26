"""Validate the persisted dataset contract before changing review state."""
import math
import struct

from ts_provider_http import redact_provider_url


class DatasetFormatError(ValueError):
    pass


def check_zip_directory(path, max_members):
    """Bound directory allocation before ZipFile constructs ZipInfo objects.

    Export-sized single-disk ZIPs only; ZIP64 and prepended executable archives
    are outside the restore contract. Expansion checks still run afterward.
    """
    with open(path, 'rb') as source:
        source.seek(0, 2)
        size = source.tell()
        tail_size = min(size, 65557)
        source.seek(size - tail_size)
        tail = source.read(tail_size)
        offset = tail.rfind(b'PK\x05\x06')
        if offset < 0 or len(tail) - offset < 22:
            raise DatasetFormatError('Invalid ZIP directory')
        _, disk, start_disk, disk_count, count, cd_size, cd_offset, comment = struct.unpack_from('<4s4H2IH', tail, offset)
        # ZipFile follows this locator even when the ordinary EOCD contains
        # plausible small counts. Reject before it can allocate ZipInfo objects.
        eocd_offset = size - tail_size + offset
        source.seek(max(0, eocd_offset - 20))
        if eocd_offset >= 20 and source.read(4) == b'PK\x06\x07':
            raise DatasetFormatError('ZIP64 datasets are not supported')
        if (disk or start_disk or disk_count != count or count > max_members
                or count == 65535 or cd_size > max_members * 4096
                or cd_offset == 0xffffffff or cd_size == 0xffffffff
                or cd_offset + cd_size != size - tail_size + offset
                or offset + 22 + comment != len(tail)):
            raise DatasetFormatError('Unsupported or oversized ZIP directory')
        source.seek(cd_offset)
        end = cd_offset + cd_size
        for _ in range(count):
            header = source.read(46)
            if len(header) != 46 or header[:4] != b'PK\x01\x02':
                raise DatasetFormatError('Invalid ZIP directory record')
            lengths = struct.unpack_from('<3H', header, 28)
            source.seek(sum(lengths), 1)
            if source.tell() > end:
                raise DatasetFormatError('Invalid ZIP directory size')
        if source.tell() != end:
            raise DatasetFormatError('ZIP directory count mismatch')


def validate_contents(contents):
    """Return a bounded, normalized schema; never modify the caller's data."""
    def require(condition):
        if not condition:
            raise DatasetFormatError('Invalid dataset metadata or result fields')

    def number(value):
        return type(value) in (int, float) and math.isfinite(value)

    def integer(value, minimum=0):
        return type(value) is int and minimum <= value <= 1000000

    def text(value):
        return isinstance(value, str) and len(value) <= 8192

    require(isinstance(contents, list) and len(contents) == 3)
    tiles, results, metadata = contents
    require(isinstance(tiles, list) and len(tiles) <= 1000)
    require(isinstance(results, list) and len(results) <= 100000)
    require(type(metadata) is bool)
    require(all(isinstance(row, dict) for row in tiles + results))
    tile_fields = {'index', 'filename', 'labelfilename', 'detections', 'metadata', 'url'}
    result_fields = {'class', 'class_name', 'x1', 'x2', 'y1', 'y2', 'conf',
                     'selected', 'inside', 'metadata', 'url', 'address',
                     'address_provider', 'address_confidence', 'secondary',
                     'id', 'tile', 'id_in_tile'}
    tiles = [{k: v for k, v in row.items() if k in tile_fields} for row in tiles]
    results = [{k: v for k, v in row.items() if k in result_fields} for row in results]
    tile_ids = set()
    for tile in tiles:
        require(isinstance(tile, dict))
        require(integer(tile.get('index')) and tile['index'] not in tile_ids)
        tile_ids.add(tile['index'])
        require(text(tile.get('filename')) and bool(tile['filename']))
        require(isinstance(tile.get('detections'), list) and len(tile['detections']) <= 10000)
        normalized_labels = []
        for label in tile['detections']:
            require(text(label))
            parts = label.split()
            try:
                values = [float(part) for part in parts]
            except ValueError:
                raise DatasetFormatError('Invalid dataset annotation') from None
            require(len(values) == 5 and values[0] == 0 and all(math.isfinite(v) and 0 <= v <= 1 for v in values))
            normalized_labels.append(' '.join(['0', *parts[1:]]) + '\n')
        tile['detections'] = normalized_labels
        for field in ('metadata', 'url', 'labelfilename'):
            if field in tile:
                require(text(tile[field]))
    tiles_by_id = {tile['index']: tile for tile in tiles}
    # The receiving cdcai writer prepended one pseudo-result per ordered tile,
    # but omitted its id. Only adapt that unambiguous layout, never mixed ids.
    pseudo_results = [row for row in results if row.get('class') == 1]
    if any('id' not in row for row in pseudo_results):
        require(len(pseudo_results) == len(tiles))
        require(all('id' not in row for row in pseudo_results))
        require([tile['index'] for tile in tiles] == list(range(len(tiles))))
        require(all(row.get('class') == 1 for row in results[:len(tiles)]))
        for index, row in enumerate(pseudo_results):
            row['id'] = index
    result_tile_ids = set()
    for result in results:
        require(isinstance(result, dict))
        require(type(result.get('class')) is int and result['class'] in (0, 1))
        require(text(result.get('class_name')))
        require(all(number(result.get(k)) for k in ('x1', 'x2', 'y1', 'y2', 'conf')))
        require(0 <= result['conf'] <= 1)
        require(all(-180 <= result[k] <= 180 for k in ('x1', 'x2')))
        require(all(-90 <= result[k] <= 90 for k in ('y1', 'y2')))
        for field in ('selected', 'inside'):
            if field in result or result['class'] == 0:
                require(type(result.get(field)) is bool)
        for field in ('metadata', 'url', 'address', 'address_provider'):
            if field in result:
                require(text(result[field]))
        for field in ('secondary', 'address_confidence'):
            if field in result:
                require(number(result[field]) and 0 <= result[field] <= 1)
        if result['class'] == 1:
            require(result['class_name'] == 'tile' and integer(result.get('id')))
            require(result['id'] in tile_ids and result['id'] not in result_tile_ids)
            result_tile_ids.add(result['id'])
        else:
            require(integer(result.get('tile')) and result['tile'] in tile_ids)
            require(integer(result.get('id_in_tile'), -1))
            tile = tiles_by_id[result['tile']]
            require(result['id_in_tile'] == -1 or result['id_in_tile'] < len(tile['detections']))
    require(result_tile_ids == tile_ids)
    for row in tiles + results:
        if 'url' in row:
            try:
                row['url'] = redact_provider_url(row['url'])
            except ValueError:
                raise DatasetFormatError('Invalid dataset provider URL') from None
    return [tiles, results, metadata]
