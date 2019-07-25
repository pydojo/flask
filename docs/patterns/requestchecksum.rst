请求内容校验和
=========================

各种代码片段可以耗尽请求数据后进行预处理。
例如在已读取和处理完的请求对象上以 JSON 数据作为结束，
表单数据也会终止于此，但通过的代码路径是不同的。
当你想要对进入的请求数据计算校验和时，这看起来就不方便了。
对于一些 APIs 来说有时计算校验和是需要的。

不管如何做到的，幸运的是通过打包成输入流就非常容易去改变。

下面的例子计算了进入数据的 SHA1 校验和，
在 WSGI 环境中获得读取数据后再存储数据::

    import hashlib

    class ChecksumCalcStream(object):

        def __init__(self, stream):
            self._stream = stream
            self._hash = hashlib.sha1()

        def read(self, bytes):
            rv = self._stream.read(bytes)
            self._hash.update(rv)
            return rv

        def readline(self, size_hint):
            rv = self._stream.readline(size_hint)
            self._hash.update(rv)
            return rv

    def generate_checksum(request):
        env = request.environ
        stream = ChecksumCalcStream(env['wsgi.input'])
        env['wsgi.input'] = stream
        return stream._hash

要使用这种方法，所有你需要做的就是在请求开始消耗数据之前，
把计算数据流用钩进来。 (例如，要小心访问 ``request.form``
或任何该性质的对象。 ``before_request_handlers``
对于此种情景应该小心地别访问它)。

示例用法::

    @app.route('/special-api', methods=['POST'])
    def special_api():
        hash = generate_checksum(request)
        # Accessing this parses the input stream
        files = request.files
        # At this point the hash is fully constructed.
        checksum = hash.hexdigest()
        return 'Hash was: %s' % checksum
