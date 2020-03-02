from typing import List
from urllib.parse import urlparse, urlunparse, ParseResult

__version__ = "0.0.1"


class S3Path(object):
    def __init__(self, s3url: str):
        self.parsed_url = urlparse(s3url)
        self._parts = self.parsed_url.path.split("/")

    @property
    def anchor(self):
        """The concatenation of the drive and root, or ''."""
        raise NotImplementedError

    @property
    def name(self):
        """The final path component, if any."""
        parts = self._parts
        return parts[-1]

    @property
    def suffix(self):
        """The final component's last suffix, if any."""
        name = self.name
        i = name.rfind('.')
        if 0 < i < len(name) - 1:
            return name[i:]
        else:
            return ''

    @property
    def suffixes(self):
        """A list of the final component's suffixes, if any."""
        name = self.name
        if name.endswith('.'):
            return []
        name = name.lstrip('.')
        return ['.' + suffix for suffix in name.split('.')[1:]]

    @property
    def stem(self):
        """The final path component, minus its last suffix."""
        name = self.name
        i = name.rfind('.')
        if 0 < i < len(name) - 1:
            return name[:i]
        else:
            return name

    def with_name(self, name):
        """Return a new path with the file name changed."""
        if not self.name:
            raise ValueError("%r has an empty name" % (self,))
        drv, root, parts = self._flavour.parse_parts((name,))
        if (not name or name[-1] in [self._flavour.sep, self._flavour.altsep]
                or drv or root or len(parts) != 1):
            raise ValueError("Invalid name %r" % (name))
        return self._from_parsed_parts(self._parts[:-1] + [name], self.parsed_url)

    def with_suffix(self, suffix):
        """Return a new path with the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix is an empty
        string, remove the suffix from the path.
        """
        f = self._flavour
        if f.sep in suffix or f.altsep and f.altsep in suffix:
            raise ValueError("Invalid suffix %r" % (suffix,))
        if suffix and not suffix.startswith('.') or suffix == '.':
            raise ValueError("Invalid suffix %r" % (suffix))
        name = self.name
        if not name:
            raise ValueError("%r has an empty name" % (self,))
        old_suffix = self.suffix
        if not old_suffix:
            name = name + suffix
        else:
            name = name[:-len(old_suffix)] + suffix
        return self._from_parsed_parts(self._parts[:-1] + [name], self.parsed_url)

    def relative_to(self, *other):
        """Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        a subpath of the other path), raise ValueError.
        """
        # For the purpose of this method, drive and root are considered
        # separate parts, i.e.:
        #   Path('c:/').relative_to('c:')  gives Path('/')
        #   Path('c:/').relative_to('/')   raise ValueError
        raise NotImplementedError()

    @property
    def parts(self):
        """An object providing sequence-like access to the
        components in the filesystem path."""
        # We cache the tuple to avoid building a new one each time .parts
        # is accessed.  XXX is this necessary?
        try:
            return self._pparts
        except AttributeError:
            self._pparts = tuple(self._parts)
            return self._pparts

    def joinpath(self, *args):
        """Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).
        """
        raise NotImplementedError

    def __truediv__(self, key):
        return self._make_child((key,))

    def __rtruediv__(self, key):
        raise NotImplementedError

    def _make_child(self, args: str):
        parts = self._parts + [args]
        return self._from_parsed_parts(parts, self.parsed_url)

    @property
    def parent(self):
        """The logical parent of the path."""
        parts = self._parts
        return self._from_parsed_parts(parts[:-1], self.parsed_url)

    @property
    def parents(self):
        """A sequence of this path's logical parents."""
        raise NotImplementedError

    def is_absolute(self):
        """True if the path is absolute (has both a root and, if applicable,
        a drive)."""
        raise NotImplementedError

    def is_reserved(self):
        """Return True if the path contains one of the special names reserved
        by the system, if any."""
        raise NotImplementedError

    def match(self, path_pattern):
        """
        Return True if this path matches the given pattern.
        """
        raise NotImplementedError

    @classmethod
    def _from_parsed_parts(cls, parts: List[str], parsed_url: ParseResult):
        parsed_url._replace(path="/".join(parts))
        url = urlunparse(parsed_url)
        return cls(url)

    def __str__(self):
        return self.parsed_url.geturl()
