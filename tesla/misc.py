def shortenPath(path, n):
    parts = path.split('/')
    return '...{}'.format('/'.join(parts[-n:])) if len(parts) > n else path
