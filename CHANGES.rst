.. currentmodule:: flask

Flask 变更日志
===============


版本 1.1
-----------

未发布

-   :meth:`flask.RequestContext.copy` includes the current session
    object in the request context copy. This prevents ``session``
    pointing to an out-of-date object. (`#2935`_)
-   Using built-in RequestContext, unprintable Unicode characters in
    Host header will result in a HTTP 400 response and not HTTP 500 as
    previously. (`#2994`_)
-   :func:`send_file` supports :class:`~os.PathLike` objects as
    described in PEP 0519, to support :mod:`pathlib` in Python 3.
    (`#3059`_)
-   :func:`send_file` supports :class:`~io.BytesIO` partial content.
    (`#2957`_)

.. _#2935: https://github.com/pallets/flask/issues/2935
.. _#2957: https://github.com/pallets/flask/issues/2957
.. _#2994: https://github.com/pallets/flask/pull/2994
.. _#3059: https://github.com/pallets/flask/pull/3059


Version 1.0.3
-------------

Unreleased

-   :func:`send_file` encodes filenames as ASCII instead of Latin-1
    (ISO-8859-1). This fixes compatibility with Gunicorn, which is
    stricter about header encodings than PEP 3333. (`#2766`_)
-   Allow custom CLIs using ``FlaskGroup`` to set the debug flag without
    it always being overwritten based on environment variables.
    (`#2765`_)
-   ``flask --version`` outputs Werkzeug's version and simplifies the
    Python version. (`#2825`_)
-   :func:`send_file` handles an ``attachment_filename`` that is a
    native Python 2 string (bytes) with UTF-8 coded bytes. (`#2933`_)
-   A catch-all error handler registered for ``HTTPException`` will not
    handle ``RoutingException``, which is used internally during
    routing. This fixes the unexpected behavior that had been introduced
    in 1.0. (`#2986`_)

.. _#2766: https://github.com/pallets/flask/issues/2766
.. _#2765: https://github.com/pallets/flask/pull/2765
.. _#2825: https://github.com/pallets/flask/pull/2825
.. _#2933: https://github.com/pallets/flask/issues/2933
.. _#2986: https://github.com/pallets/flask/pull/2986


Version 1.0.2
-------------

Released on May 2nd 2018

-   Fix more backwards compatibility issues with merging slashes between
    a blueprint prefix and route. (`#2748`_)
-   Fix error with ``flask routes`` command when there are no routes.
    (`#2751`_)

.. _#2748: https://github.com/pallets/flask/pull/2748
.. _#2751: https://github.com/pallets/flask/issues/2751


Version 1.0.1
-------------

Released on April 29th 2018

-   Fix registering partials (with no ``__name__``) as view functions.
    (`#2730`_)
-   Don't treat lists returned from view functions the same as tuples.
    Only tuples are interpreted as response data. (`#2736`_)
-   Extra slashes between a blueprint's ``url_prefix`` and a route URL
    are merged. This fixes some backwards compatibility issues with the
    change in 1.0. (`#2731`_, `#2742`_)
-   Only trap ``BadRequestKeyError`` errors in debug mode, not all
    ``BadRequest`` errors. This allows ``abort(400)`` to continue
    working as expected. (`#2735`_)
-   The ``FLASK_SKIP_DOTENV`` environment variable can be set to ``1``
    to skip automatically loading dotenv files. (`#2722`_)

.. _#2722: https://github.com/pallets/flask/issues/2722
.. _#2730: https://github.com/pallets/flask/pull/2730
.. _#2731: https://github.com/pallets/flask/issues/2731
.. _#2735: https://github.com/pallets/flask/issues/2735
.. _#2736: https://github.com/pallets/flask/issues/2736
.. _#2742: https://github.com/pallets/flask/issues/2742


Version 1.0
-----------

Released on April 26th 2018

-   **Python 2.6 and 3.3 are no longer supported.** (`pallets/meta#24`_)
-   Bump minimum dependency versions to the latest stable versions:
    Werkzeug >= 0.14, Jinja >= 2.10, itsdangerous >= 0.24, Click >= 5.1.
    (`#2586`_)
-   Skip :meth:`app.run <Flask.run>` when a Flask application is run
    from the command line. This avoids some behavior that was confusing
    to debug.
-   Change the default for :data:`JSONIFY_PRETTYPRINT_REGULAR` to
    ``False``. :func:`~json.jsonify` returns a compact format by
    default, and an indented format in debug mode. (`#2193`_)
-   :meth:`Flask.__init__ <Flask>` accepts the ``host_matching``
    argument and sets it on :attr:`~Flask.url_map`. (`#1559`_)
-   :meth:`Flask.__init__ <Flask>` accepts the ``static_host`` argument
    and passes it as the ``host`` argument when defining the static
    route. (`#1559`_)
-   :func:`send_file` supports Unicode in ``attachment_filename``.
    (`#2223`_)
-   Pass ``_scheme`` argument from :func:`url_for` to
    :meth:`~Flask.handle_url_build_error`. (`#2017`_)
-   :meth:`~Flask.add_url_rule` accepts the
    ``provide_automatic_options`` argument to disable adding the
    ``OPTIONS`` method. (`#1489`_)
-   :class:`~views.MethodView` subclasses inherit method handlers from
    base classes. (`#1936`_)
-   Errors caused while opening the session at the beginning of the
    request are handled by the app's error handlers. (`#2254`_)
-   Blueprints gained :attr:`~Blueprint.json_encoder` and
    :attr:`~Blueprint.json_decoder` attributes to override the app's
    encoder and decoder. (`#1898`_)
-   :meth:`Flask.make_response` raises ``TypeError`` instead of
    ``ValueError`` for bad response types. The error messages have been
    improved to describe why the type is invalid. (`#2256`_)
-   Add ``routes`` CLI command to output routes registered on the
    application. (`#2259`_)
-   Show warning when session cookie domain is a bare hostname or an IP
    address, as these may not behave properly in some browsers, such as
    Chrome. (`#2282`_)
-   Allow IP address as exact session cookie domain. (`#2282`_)
-   ``SESSION_COOKIE_DOMAIN`` is set if it is detected through
    ``SERVER_NAME``. (`#2282`_)
-   Auto-detect zero-argument app factory called ``create_app`` or
    ``make_app`` from ``FLASK_APP``. (`#2297`_)
-   Factory functions are not required to take a ``script_info``
    parameter to work with the ``flask`` command. If they take a single
    parameter or a parameter named ``script_info``, the
    :class:`~cli.ScriptInfo` object will be passed. (`#2319`_)
-   ``FLASK_APP`` can be set to an app factory, with arguments if
    needed, for example ``FLASK_APP=myproject.app:create_app('dev')``.
    (`#2326`_)
-   ``FLASK_APP`` can point to local packages that are not installed in
    editable mode, although ``pip install -e`` is still preferred.
    (`#2414`_)
-   The :class:`~views.View` class attribute
    :attr:`~views.View.provide_automatic_options` is set in
    :meth:`~views.View.as_view`, to be detected by
    :meth:`~Flask.add_url_rule`. (`#2316`_)
-   Error handling will try handlers registered for ``blueprint, code``,
    ``app, code``, ``blueprint, exception``, ``app, exception``.
    (`#2314`_)
-   ``Cookie`` is added to the response's ``Vary`` header if the session
    is accessed at all during the request (and not deleted). (`#2288`_)
-   :meth:`~Flask.test_request_context` accepts ``subdomain`` and
    ``url_scheme`` arguments for use when building the base URL.
    (`#1621`_)
-   Set :data:`APPLICATION_ROOT` to ``'/'`` by default. This was already
    the implicit default when it was set to ``None``.
-   :data:`TRAP_BAD_REQUEST_ERRORS` is enabled by default in debug mode.
    ``BadRequestKeyError`` has a message with the bad key in debug mode
    instead of the generic bad request message. (`#2348`_)
-   Allow registering new tags with
    :class:`~json.tag.TaggedJSONSerializer` to support storing other
    types in the session cookie. (`#2352`_)
-   Only open the session if the request has not been pushed onto the
    context stack yet. This allows :func:`~stream_with_context`
    generators to access the same session that the containing view uses.
    (`#2354`_)
-   Add ``json`` keyword argument for the test client request methods.
    This will dump the given object as JSON and set the appropriate
    content type. (`#2358`_)
-   Extract JSON handling to a mixin applied to both the
    :class:`Request` and :class:`Response` classes. This adds the
    :meth:`~Response.is_json` and :meth:`~Response.get_json` methods to
    the response to make testing JSON response much easier. (`#2358`_)
-   Removed error handler caching because it caused unexpected results
    for some exception inheritance hierarchies. Register handlers
    explicitly for each exception if you want to avoid traversing the
    MRO. (`#2362`_)
-   Fix incorrect JSON encoding of aware, non-UTC datetimes. (`#2374`_)
-   Template auto reloading will honor debug mode even even if
    :attr:`~Flask.jinja_env` was already accessed. (`#2373`_)
-   The following old deprecated code was removed. (`#2385`_)

    -   ``flask.ext`` - import extensions directly by their name instead
        of through the ``flask.ext`` namespace. For example,
        ``import flask.ext.sqlalchemy`` becomes
        ``import flask_sqlalchemy``.
    -   ``Flask.init_jinja_globals`` - extend
        :meth:`Flask.create_jinja_environment` instead.
    -   ``Flask.error_handlers`` - tracked by
        :attr:`Flask.error_handler_spec`, use :meth:`Flask.errorhandler`
        to register handlers.
    -   ``Flask.request_globals_class`` - use
        :attr:`Flask.app_ctx_globals_class` instead.
    -   ``Flask.static_path`` - use :attr:`Flask.static_url_path`
        instead.
    -   ``Request.module`` - use :attr:`Request.blueprint` instead.

-   The :attr:`Request.json` property is no longer deprecated.
    (`#1421`_)
-   Support passing a :class:`~werkzeug.test.EnvironBuilder` or
    ``dict`` to :meth:`test_client.open <werkzeug.test.Client.open>`.
    (`#2412`_)
-   The ``flask`` command and :meth:`Flask.run` will load environment
    variables from ``.env`` and ``.flaskenv`` files if python-dotenv is
    installed. (`#2416`_)
-   When passing a full URL to the test client, the scheme in the URL is
    used instead of :data:`PREFERRED_URL_SCHEME`. (`#2430`_)
-   :attr:`Flask.logger` has been simplified. ``LOGGER_NAME`` and
    ``LOGGER_HANDLER_POLICY`` config was removed. The logger is always
    named ``flask.app``. The level is only set on first access, it
    doesn't check :attr:`Flask.debug` each time. Only one format is
    used, not different ones depending on :attr:`Flask.debug`. No
    handlers are removed, and a handler is only added if no handlers are
    already configured. (`#2436`_)
-   Blueprint view function names may not contain dots. (`#2450`_)
-   Fix a ``ValueError`` caused by invalid ``Range`` requests in some
    cases. (`#2526`_)
-   The development server uses threads by default. (`#2529`_)
-   Loading config files with ``silent=True`` will ignore
    :data:`~errno.ENOTDIR` errors. (`#2581`_)
-   Pass ``--cert`` and ``--key`` options to ``flask run`` to run the
    development server over HTTPS. (`#2606`_)
-   Added :data:`SESSION_COOKIE_SAMESITE` to control the ``SameSite``
    attribute on the session cookie. (`#2607`_)
-   Added :meth:`~flask.Flask.test_cli_runner` to create a Click runner
    that can invoke Flask CLI commands for testing. (`#2636`_)
-   Subdomain matching is disabled by default and setting
    :data:`SERVER_NAME` does not implicitly enable it. It can be enabled
    by passing ``subdomain_matching=True`` to the ``Flask`` constructor.
    (`#2635`_)
-   A single trailing slash is stripped from the blueprint
    ``url_prefix`` when it is registered with the app. (`#2629`_)
-   :meth:`Request.get_json` doesn't cache the
    result if parsing fails when ``silent`` is true. (`#2651`_)
-   :func:`Request.get_json` no longer accepts arbitrary encodings.
    Incoming JSON should be encoded using UTF-8 per :rfc:`8259`, but
    Flask will autodetect UTF-8, -16, or -32. (`#2691`_)
-   Added :data:`MAX_COOKIE_SIZE` and :attr:`Response.max_cookie_size`
    to control when Werkzeug warns about large cookies that browsers may
    ignore. (`#2693`_)
-   Updated documentation theme to make docs look better in small
    windows. (`#2709`_)
-   Rewrote the tutorial docs and example project to take a more
    structured approach to help new users avoid common pitfalls.
    (`#2676`_)

.. _pallets/meta#24: https://github.com/pallets/meta/issues/24
.. _#1421: https://github.com/pallets/flask/issues/1421
.. _#1489: https://github.com/pallets/flask/pull/1489
.. _#1559: https://github.com/pallets/flask/issues/1559
.. _#1621: https://github.com/pallets/flask/pull/1621
.. _#1898: https://github.com/pallets/flask/pull/1898
.. _#1936: https://github.com/pallets/flask/pull/1936
.. _#2017: https://github.com/pallets/flask/pull/2017
.. _#2193: https://github.com/pallets/flask/pull/2193
.. _#2223: https://github.com/pallets/flask/pull/2223
.. _#2254: https://github.com/pallets/flask/pull/2254
.. _#2256: https://github.com/pallets/flask/pull/2256
.. _#2259: https://github.com/pallets/flask/pull/2259
.. _#2282: https://github.com/pallets/flask/pull/2282
.. _#2288: https://github.com/pallets/flask/pull/2288
.. _#2297: https://github.com/pallets/flask/pull/2297
.. _#2314: https://github.com/pallets/flask/pull/2314
.. _#2316: https://github.com/pallets/flask/pull/2316
.. _#2319: https://github.com/pallets/flask/pull/2319
.. _#2326: https://github.com/pallets/flask/pull/2326
.. _#2348: https://github.com/pallets/flask/pull/2348
.. _#2352: https://github.com/pallets/flask/pull/2352
.. _#2354: https://github.com/pallets/flask/pull/2354
.. _#2358: https://github.com/pallets/flask/pull/2358
.. _#2362: https://github.com/pallets/flask/pull/2362
.. _#2374: https://github.com/pallets/flask/pull/2374
.. _#2373: https://github.com/pallets/flask/pull/2373
.. _#2385: https://github.com/pallets/flask/issues/2385
.. _#2412: https://github.com/pallets/flask/pull/2412
.. _#2414: https://github.com/pallets/flask/pull/2414
.. _#2416: https://github.com/pallets/flask/pull/2416
.. _#2430: https://github.com/pallets/flask/pull/2430
.. _#2436: https://github.com/pallets/flask/pull/2436
.. _#2450: https://github.com/pallets/flask/pull/2450
.. _#2526: https://github.com/pallets/flask/issues/2526
.. _#2529: https://github.com/pallets/flask/pull/2529
.. _#2586: https://github.com/pallets/flask/issues/2586
.. _#2581: https://github.com/pallets/flask/pull/2581
.. _#2606: https://github.com/pallets/flask/pull/2606
.. _#2607: https://github.com/pallets/flask/pull/2607
.. _#2636: https://github.com/pallets/flask/pull/2636
.. _#2635: https://github.com/pallets/flask/pull/2635
.. _#2629: https://github.com/pallets/flask/pull/2629
.. _#2651: https://github.com/pallets/flask/issues/2651
.. _#2676: https://github.com/pallets/flask/pull/2676
.. _#2691: https://github.com/pallets/flask/pull/2691
.. _#2693: https://github.com/pallets/flask/pull/2693
.. _#2709: https://github.com/pallets/flask/pull/2709


Version 0.12.4
--------------

Released on April 29 2018

-   Repackage 0.12.3 to fix package layout issue. (`#2728`_)

.. _#2728: https://github.com/pallets/flask/issues/2728


Version 0.12.3
--------------

Released on April 26th 2018

-   :func:`Request.get_json` no longer accepts arbitrary encodings.
    Incoming JSON should be encoded using UTF-8 per :rfc:`8259`, but
    Flask will autodetect UTF-8, -16, or -32. (`#2692`_)
-   Fix a Python warning about imports when using ``python -m flask``.
    (`#2666`_)
-   Fix a ``ValueError`` caused by invalid ``Range`` requests in some
    cases.

.. _#2666: https://github.com/pallets/flask/issues/2666
.. _#2692: https://github.com/pallets/flask/issues/2692


Version 0.12.2
--------------

Released on May 16 2017

- Fix a bug in `safe_join` on Windows.

Version 0.12.1
--------------

Bugfix release, released on March 31st 2017

- Prevent `flask run` from showing a NoAppException when an ImportError occurs
  within the imported application module.
- Fix encoding behavior of ``app.config.from_pyfile`` for Python 3. Fix
  ``#2118``.
- Use the ``SERVER_NAME`` config if it is present as default values for
  ``app.run``. ``#2109``, ``#2152``
- Call `ctx.auto_pop` with the exception object instead of `None`, in the
  event that a `BaseException` such as `KeyboardInterrupt` is raised in a
  request handler.

Version 0.12
------------

Released on December 21st 2016, codename Punsch.

- the cli command now responds to `--version`.
- Mimetype guessing and ETag generation for file-like objects in ``send_file``
  has been removed, as per issue ``#104``. (`#1849`_)
- Mimetype guessing in ``send_file`` now fails loudly and doesn't fall back to
  ``application/octet-stream``. (`#1988`_)
- Make ``flask.safe_join`` able to join multiple paths like ``os.path.join``
  (`#1730`_).
- Revert a behavior change that made the dev server crash instead of returning
  an Internal Server Error (`#2006`_).
- Correctly invoke response handlers for both regular request dispatching as
  well as error handlers.
- Disable logger propagation by default for the app logger.
- Add support for range requests in ``send_file``.
- ``app.test_client`` includes preset default environment, which can now be
  directly set, instead of per ``client.get``.

.. _#1849: https://github.com/pallets/flask/pull/1849
.. _#1988: https://github.com/pallets/flask/pull/1988
.. _#1730: https://github.com/pallets/flask/pull/1730
.. _#2006: https://github.com/pallets/flask/pull/2006

Version 0.11.2
--------------

Bugfix release, unreleased

- Fix crash when running under PyPy3. (`#1814`_)

.. _#1814: https://github.com/pallets/flask/pull/1814

Version 0.11.1
--------------

Bugfix release, released on June 7th 2016.

- Fixed a bug that prevented ``FLASK_APP=foobar/__init__.py`` from working. (`#1872`_)

.. _#1872: https://github.com/pallets/flask/pull/1872

Version 0.11
------------

Released on May 29th 2016, codename Absinthe.

- Added support to serializing top-level arrays to :func:`flask.jsonify`. This
  introduces a security risk in ancient browsers. See
  :ref:`json-security` for details.
- Added before_render_template signal.
- Added `**kwargs` to :meth:`flask.Test.test_client` to support passing
  additional keyword arguments to the constructor of
  :attr:`flask.Flask.test_client_class`.
- Added ``SESSION_REFRESH_EACH_REQUEST`` config key that controls the
  set-cookie behavior.  If set to ``True`` a permanent session will be
  refreshed each request and get their lifetime extended, if set to
  ``False`` it will only be modified if the session actually modifies.
  Non permanent sessions are not affected by this and will always
  expire if the browser window closes.
- Made Flask support custom JSON mimetypes for incoming data.
- Added support for returning tuples in the form ``(response, headers)``
  from a view function.
- Added :meth:`flask.Config.from_json`.
- Added :attr:`flask.Flask.config_class`.
- Added :meth:`flask.Config.get_namespace`.
- Templates are no longer automatically reloaded outside of debug mode. This
  can be configured with the new ``TEMPLATES_AUTO_RELOAD`` config key.
- Added a workaround for a limitation in Python 3.3's namespace loader.
- Added support for explicit root paths when using Python 3.3's namespace
  packages.
- Added :command:`flask` and the ``flask.cli`` module to start the local
  debug server through the click CLI system.  This is recommended over the old
  ``flask.run()`` method as it works faster and more reliable due to a
  different design and also replaces ``Flask-Script``.
- Error handlers that match specific classes are now checked first,
  thereby allowing catching exceptions that are subclasses of HTTP
  exceptions (in ``werkzeug.exceptions``).  This makes it possible
  for an extension author to create exceptions that will by default
  result in the HTTP error of their choosing, but may be caught with
  a custom error handler if desired.
- Added :meth:`flask.Config.from_mapping`.
- Flask will now log by default even if debug is disabled.  The log format is
  now hardcoded but the default log handling can be disabled through the
  ``LOGGER_HANDLER_POLICY`` configuration key.
- Removed deprecated module functionality.
- Added the ``EXPLAIN_TEMPLATE_LOADING`` config flag which when enabled will
  instruct Flask to explain how it locates templates.  This should help
  users debug when the wrong templates are loaded.
- Enforce blueprint handling in the order they were registered for template
  loading.
- Ported test suite to py.test.
- Deprecated ``request.json`` in favour of ``request.get_json()``.
- Add "pretty" and "compressed" separators definitions in jsonify() method.
  Reduces JSON response size when JSONIFY_PRETTYPRINT_REGULAR=False by removing
  unnecessary white space included by default after separators.
- JSON responses are now terminated with a newline character, because it is a
  convention that UNIX text files end with a newline and some clients don't
  deal well when this newline is missing. See
  https://github.com/pallets/flask/pull/1262 -- this came up originally as a
  part of https://github.com/kennethreitz/httpbin/issues/168
- The automatically provided ``OPTIONS`` method is now correctly disabled if
  the user registered an overriding rule with the lowercase-version
  ``options`` (issue ``#1288``).
- ``flask.json.jsonify`` now supports the ``datetime.date`` type (`#1326`_).
- Don't leak exception info of already catched exceptions to context teardown
  handlers (`#1393`_).
- Allow custom Jinja environment subclasses (`#1422`_).
- Updated extension dev guidelines.

- ``flask.g`` now has ``pop()`` and ``setdefault`` methods.
- Turn on autoescape for ``flask.templating.render_template_string`` by default
  (`#1515`_).
- ``flask.ext`` is now deprecated (`#1484`_).
- ``send_from_directory`` now raises BadRequest if the filename is invalid on
  the server OS (`#1763`_).
- Added the ``JSONIFY_MIMETYPE`` configuration variable (`#1728`_).
- Exceptions during teardown handling will no longer leave bad application
  contexts lingering around.

.. _#1326: https://github.com/pallets/flask/pull/1326
.. _#1393: https://github.com/pallets/flask/pull/1393
.. _#1422: https://github.com/pallets/flask/pull/1422
.. _#1515: https://github.com/pallets/flask/pull/1515
.. _#1484: https://github.com/pallets/flask/pull/1484
.. _#1763: https://github.com/pallets/flask/pull/1763
.. _#1728: https://github.com/pallets/flask/pull/1728

Version 0.10.2
--------------

(bugfix release, release date to be announced)

- Fixed broken `test_appcontext_signals()` test case.
- Raise an :exc:`AttributeError` in :func:`flask.helpers.find_package` with a
  useful message explaining why it is raised when a PEP 302 import hook is used
  without an `is_package()` method.
- Fixed an issue causing exceptions raised before entering a request or app
  context to be passed to teardown handlers.
- Fixed an issue with query parameters getting removed from requests in
  the test client when absolute URLs were requested.
- Made `@before_first_request` into a decorator as intended.
- Fixed an etags bug when sending a file streams with a name.
- Fixed `send_from_directory` not expanding to the application root path
  correctly.
- Changed logic of before first request handlers to flip the flag after
  invoking.  This will allow some uses that are potentially dangerous but
  should probably be permitted.
- Fixed Python 3 bug when a handler from `app.url_build_error_handlers`
  reraises the `BuildError`.

Version 0.10.1
--------------

(bugfix release, released on June 14th 2013)

- Fixed an issue where ``|tojson`` was not quoting single quotes which
  made the filter not work properly in HTML attributes.  Now it's
  possible to use that filter in single quoted attributes.  This should
  make using that filter with angular.js easier.
- Added support for byte strings back to the session system.  This broke
  compatibility with the common case of people putting binary data for
  token verification into the session.
- Fixed an issue where registering the same method twice for the same endpoint
  would trigger an exception incorrectly.

Version 0.10
------------

Released on June 13th 2013, codename Limoncello.

- Changed default cookie serialization format from pickle to JSON to
  limit the impact an attacker can do if the secret key leaks.  See
  :ref:`upgrading-to-010` for more information.
- Added ``template_test`` methods in addition to the already existing
  ``template_filter`` method family.
- Added ``template_global`` methods in addition to the already existing
  ``template_filter`` method family.
- Set the content-length header for x-sendfile.
- ``tojson`` filter now does not escape script blocks in HTML5 parsers.
- ``tojson`` used in templates is now safe by default due.  This was
  allowed due to the different escaping behavior.
- Flask will now raise an error if you attempt to register a new function
  on an already used endpoint.
- Added wrapper module around simplejson and added default serialization
  of datetime objects.  This allows much easier customization of how
  JSON is handled by Flask or any Flask extension.
- Removed deprecated internal ``flask.session`` module alias.  Use
  ``flask.sessions`` instead to get the session module.  This is not to
  be confused with ``flask.session`` the session proxy.
- Templates can now be rendered without request context.  The behavior is
  slightly different as the ``request``, ``session`` and ``g`` objects
  will not be available and blueprint's context processors are not
  called.
- The config object is now available to the template as a real global and
  not through a context processor which makes it available even in imported
  templates by default.
- Added an option to generate non-ascii encoded JSON which should result
  in less bytes being transmitted over the network.  It's disabled by
  default to not cause confusion with existing libraries that might expect
  ``flask.json.dumps`` to return bytestrings by default.
- ``flask.g`` is now stored on the app context instead of the request
  context.
- ``flask.g`` now gained a ``get()`` method for not erroring out on non
  existing items.
- ``flask.g`` now can be used with the ``in`` operator to see what's defined
  and it now is iterable and will yield all attributes stored.
- ``flask.Flask.request_globals_class`` got renamed to
  ``flask.Flask.app_ctx_globals_class`` which is a better name to what it
  does since 0.10.
- `request`, `session` and `g` are now also added as proxies to the template
  context which makes them available in imported templates.  One has to be
  very careful with those though because usage outside of macros might
  cause caching.
- Flask will no longer invoke the wrong error handlers if a proxy
  exception is passed through.
- Added a workaround for chrome's cookies in localhost not working
  as intended with domain names.
- Changed logic for picking defaults for cookie values from sessions
  to work better with Google Chrome.
- Added `message_flashed` signal that simplifies flashing testing.
- Added support for copying of request contexts for better working with
  greenlets.
- Removed custom JSON HTTP exception subclasses.  If you were relying on them
  you can reintroduce them again yourself trivially.  Using them however is
  strongly discouraged as the interface was flawed.
- Python requirements changed: requiring Python 2.6 or 2.7 now to prepare
  for Python 3.3 port.
- Changed how the teardown system is informed about exceptions.  This is now
  more reliable in case something handles an exception halfway through
  the error handling process.
- Request context preservation in debug mode now keeps the exception
  information around which means that teardown handlers are able to
  distinguish error from success cases.
- Added the ``JSONIFY_PRETTYPRINT_REGULAR`` configuration variable.
- Flask now orders JSON keys by default to not trash HTTP caches due to
  different hash seeds between different workers.
- Added `appcontext_pushed` and `appcontext_popped` signals.
- The builtin run method now takes the ``SERVER_NAME`` into account when
  picking the default port to run on.
- Added `flask.request.get_json()` as a replacement for the old
  `flask.request.json` property.

Version 0.9
-----------

Released on July 1st 2012, codename Campari.

- The :func:`flask.Request.on_json_loading_failed` now returns a JSON formatted
  response by default.
- The :func:`flask.url_for` function now can generate anchors to the
  generated links.
- The :func:`flask.url_for` function now can also explicitly generate
  URL rules specific to a given HTTP method.
- Logger now only returns the debug log setting if it was not set
  explicitly.
- Unregister a circular dependency between the WSGI environment and
  the request object when shutting down the request.  This means that
  environ ``werkzeug.request`` will be ``None`` after the response was
  returned to the WSGI server but has the advantage that the garbage
  collector is not needed on CPython to tear down the request unless
  the user created circular dependencies themselves.
- Session is now stored after callbacks so that if the session payload
  is stored in the session you can still modify it in an after
  request callback.
- The :class:`flask.Flask` class will avoid importing the provided import name
  if it can (the required first parameter), to benefit tools which build Flask
  instances programmatically.  The Flask class will fall back to using import
  on systems with custom module hooks, e.g. Google App Engine, or when the
  import name is inside a zip archive (usually a .egg) prior to Python 2.7.
- Blueprints now have a decorator to add custom template filters application
  wide, :meth:`flask.Blueprint.app_template_filter`.
- The Flask and Blueprint classes now have a non-decorator method for adding
  custom template filters application wide,
  :meth:`flask.Flask.add_template_filter` and
  :meth:`flask.Blueprint.add_app_template_filter`.
- The :func:`flask.get_flashed_messages` function now allows rendering flashed
  message categories in separate blocks, through a ``category_filter``
  argument.
- The :meth:`flask.Flask.run` method now accepts ``None`` for `host` and `port`
  arguments, using default values when ``None``.  This allows for calling run
  using configuration values, e.g. ``app.run(app.config.get('MYHOST'),
  app.config.get('MYPORT'))``, with proper behavior whether or not a config
  file is provided.
- The :meth:`flask.render_template` method now accepts a either an iterable of
  template names or a single template name.  Previously, it only accepted a
  single template name.  On an iterable, the first template found is rendered.
- Added :meth:`flask.Flask.app_context` which works very similar to the
  request context but only provides access to the current application.  This
  also adds support for URL generation without an active request context.
- View functions can now return a tuple with the first instance being an
  instance of :class:`flask.Response`.  This allows for returning
  ``jsonify(error="error msg"), 400`` from a view function.
- :class:`~flask.Flask` and :class:`~flask.Blueprint` now provide a
  :meth:`~flask.Flask.get_send_file_max_age` hook for subclasses to override
  behavior of serving static files from Flask when using
  :meth:`flask.Flask.send_static_file` (used for the default static file
  handler) and :func:`~flask.helpers.send_file`.  This hook is provided a
  filename, which for example allows changing cache controls by file extension.
  The default max-age for `send_file` and static files can be configured
  through a new ``SEND_FILE_MAX_AGE_DEFAULT`` configuration variable, which is
  used in the default `get_send_file_max_age` implementation.
- Fixed an assumption in sessions implementation which could break message
  flashing on sessions implementations which use external storage.
- Changed the behavior of tuple return values from functions.  They are no
  longer arguments to the response object, they now have a defined meaning.
- Added :attr:`flask.Flask.request_globals_class` to allow a specific class to
  be used on creation of the :data:`~flask.g` instance of each request.
- Added `required_methods` attribute to view functions to force-add methods
  on registration.
- Added :func:`flask.after_this_request`.
- Added :func:`flask.stream_with_context` and the ability to push contexts
  multiple times without producing unexpected behavior.

Version 0.8.1
-------------

Bugfix release, released on July 1st 2012

- Fixed an issue with the undocumented `flask.session` module to not
  work properly on Python 2.5.  It should not be used but did cause
  some problems for package managers.

Version 0.8
-----------

Released on September 29th 2011, codename Rakija

- Refactored session support into a session interface so that
  the implementation of the sessions can be changed without
  having to override the Flask class.
- Empty session cookies are now deleted properly automatically.
- View functions can now opt out of getting the automatic
  OPTIONS implementation.
- HTTP exceptions and Bad Request errors can now be trapped so that they
  show up normally in the traceback.
- Flask in debug mode is now detecting some common problems and tries to
  warn you about them.
- Flask in debug mode will now complain with an assertion error if a view
  was attached after the first request was handled.  This gives earlier
  feedback when users forget to import view code ahead of time.
- Added the ability to register callbacks that are only triggered once at
  the beginning of the first request. (:meth:`Flask.before_first_request`)
- Malformed JSON data will now trigger a bad request HTTP exception instead
  of a value error which usually would result in a 500 internal server
  error if not handled.  This is a backwards incompatible change.
- Applications now not only have a root path where the resources and modules
  are located but also an instance path which is the designated place to
  drop files that are modified at runtime (uploads etc.).  Also this is
  conceptually only instance depending and outside version control so it's
  the perfect place to put configuration files etc.  For more information
  see :ref:`instance-folders`.
- Added the ``APPLICATION_ROOT`` configuration variable.
- Implemented :meth:`~flask.testing.TestClient.session_transaction` to
  easily modify sessions from the test environment.
- Refactored test client internally.  The ``APPLICATION_ROOT`` configuration
  variable as well as ``SERVER_NAME`` are now properly used by the test client
  as defaults.
- Added :attr:`flask.views.View.decorators` to support simpler decorating of
  pluggable (class-based) views.
- Fixed an issue where the test client if used with the "with" statement did not
  trigger the execution of the teardown handlers.
- Added finer control over the session cookie parameters.
- HEAD requests to a method view now automatically dispatch to the `get`
  method if no handler was implemented.
- Implemented the virtual :mod:`flask.ext` package to import extensions from.
- The context preservation on exceptions is now an integral component of
  Flask itself and no longer of the test client.  This cleaned up some
  internal logic and lowers the odds of runaway request contexts in unittests.

Version 0.7.3
-------------

Bugfix release, release date to be decided

- Fixed the Jinja2 environment's list_templates method not returning the
  correct names when blueprints or modules were involved.

Version 0.7.2
-------------

Bugfix release, released on July 6th 2011

- Fixed an issue with URL processors not properly working on
  blueprints.

Version 0.7.1
-------------

Bugfix release, released on June 29th 2011

- Added missing future import that broke 2.5 compatibility.
- Fixed an infinite redirect issue with blueprints.

版本 0.7
-----------

发布于 June 28th 2011，代号 Grappa 白兰地

- 已加入 :meth:`~flask.Flask.make_default_options_response` 方法，
  该方法可以用于子类来警告 ``OPTIONS`` 响应的默认行为。
- 解绑本地现在会产生一个正确的 :exc:`RuntimeError` 运行错误来代替一个
  :exc:`AttributeError` 属性错误。
- 对于 :func:`flask.send_file` 函数淘汰了媒体类型的猜测和电子标签支持，
  因为猜猜是不可靠的。代入文件名或写你自己的电子标签后通过手动提供一个正确
  的媒体类型。
- 对于模块来说静态文件处理现在需要提供明确的静态文件夹名。以前自动检测是
  不可靠的，并且在 Google 的应用引擎上会产生问题。直到 1.0 老旧的表现
  依然会存在，但会有依赖警告。
- 修复一个运行在 jython 上的 Flask 问题。
- 已加入一个 ``PROPAGATE_EXCEPTIONS`` 配置变量，这个变量可以用来翻页
  例外传播设置，以前的例外传播设置只会连接到 ``DEBUG`` 上，而现在既可以
  连接到 ``DEBUG`` 模式上，也可以连接到 ``TESTING`` 测试模式上。
- Flask 不再内部依靠通过 `add_url_rule` 函数增加的规则，并且现在可以
  接受常规的 werkzeug 规则加入到 url 地图中。
- 已加入一个 `endpoint` 方法给 flask 应用对象，这样允许一个对象注册一个
  回调给任何一个带有一个装饰器的端点。
- 使用最后编辑日期给静态文件发送，这样代替了 0.6 中介绍的不正确发送日期。
- 已加入 `create_jinja_loader` 来覆写加载器建立的进程。
- 为 `config.from_pyfile` 部署一个沉默旗语。
- 已加入 `teardown_request` 装饰器，对那些应该运行在一个请求结束时考虑
  是否有一个例外发生。同样对于 `after_request` 的表现也有了变更。当一个
  例外产生时它现在不再执行了。查看 :ref:`upgrading-to-new-teardown-handling`
- 已部署 :func:`flask.has_request_context` 函数。
- 淘汰了 `init_jinja_globals` 方法。覆写 :meth:`~flask.Flask.create_jinja_environment` 
  方法来代替同样的功能。
- 已加入 :func:`flask.safe_join` 函数。
- 自动化 JSON 请求数据解压现在会查看媒体类型参数字符集。
- 如果在会话里没有消息的话，不会修改 :func:`flask.get_flashed_messages` 函数
  上的会话。
- `before_request` 处理器现在能够用错误来忽略请求。
- 不再支持定义用户例外处理器。在请求处理过程中你可以为某种可能发生的错误提供
  来自一个中心 hub 的自定义错误消息 (例如，对于数据库连接实例错误来说，远程
  资源超时错误，等等)。
- 蓝图技术可以提供蓝图具体的错误处理器。
- 已部署普通的 :ref:`views` 视图函数(基于类的视图函数)。

版本 0.6.1
-------------

Bug 修复，发布于 December 31st 2010

- 修复了一个默认 ``OPTIONS`` 响应没有曝露 ``Allow`` 头部中所有合法方法的 bug
- Jinja2 模版加载句法现在允许在一个模版加载路径里使用 "./" 写法。以前使用模块
  配置会有问题。
- 修复了一个为模块配置子域名会忽略静态文件夹的问题。
- 修复一个安全问题，问题是如果主机服务器是 Windows 操作系统的话客户端会下载任何文件，
  并且客户端使用反斜杠转义目录会导致文件暴露出来。

版本 0.6
-----------

发布于 July 27th 2010，代号 Whisky 威士忌

- 在请求函数之后就可以用逆序注册来调用这些请求函数。
- OPTIONS 现在是由 Flask 自动部署，除非应用明确增加 'OPTIONS'
  方法到 URL 规则中。在这种情况下 OPTIONS 处理不会自动介入。
- 对于模块来说如果没有静态文件夹的话，静态规则依然存在。这
  样做是为了 GAE，因为如果静态文件夹映射在 .yml 文件中的话，
  GAE会删除静态文件夹。
- :attr:`~flask.Flask.config` 属性现在可以用在模版中
  作为 `config` 内容。
- 语境处理器不再会覆写直接带入到翻译函数中的那些值了。
- 已加入限制入口请求数据含带新 ``MAX_CONTENT_LENGTH`` 
  配置值的能力。
- :meth:`flask.Module.add_url_rule` 方法的端点可选为
  与应用对象上同名函数保持一致了。
- 已加入一个 :func:`flask.make_response` 函数，它直接
  在视图函数中建立响应对象实例。
- 已加入基于信号灯的信号支持。这个特性当前是可选项，并且可
  能会由扩展与应用来使用。如果你想用这个特性的话，确保已经
  安装了 `blinker`_ 库。
- 重构了 URL 适配器建立的方法。这种重构处理现在完全可以用
  :meth:`~flask.Flask.create_url_adapter` 方法来自定
  义了。
- 模块现在可以注册一个子域名来代替一个 URL 前缀。这样做可以
  把一个完整的模块绑定到一个可配置的子域名上。

.. _blinker: https://pypi.org/project/blinker/

版本 0.5.2
-------------

Bug 修复，发布于 July 15th 2010

- 修复另一个从目录加载模版的问题，从而解决了什么时候模块用在哪里。
  modules were used.

版本 0.5.1
-------------

Bug 修复，发布于 July 6th 2010

- 修复一个模版加载目录的问题，从而解决了什么时候模块用在哪里。

版本 0.5
-----------

发布于 July 6th 2010，代号 Calvados 烈酒

- 修复了一个 bug 该 bug 是不能访问具体服务器名的子域名。服务器名现在可以
  用 ``SERVER_NAME`` 配置键来设置了。这个键名现在也用来设置会话 cookie
  跨子域名功能。
- 自动转义不再为所有模版处于激活状态。相反自动转义只为 ``.html``、 ``.htm``、
  ``.xml`` 和 ``.xhtml`` 而激活。在这些模版中自动转义的行为可以用
  ``autoescape`` 模版语言标签来改变。
- 内部重构完 Flask 代码。现在是由多个文件组成的了。
- :func:`flask.send_file` 函数此时发出许多电子标签后具备了内在的条件反射能力。
- (临时地) 删除了压缩应用程序的支持。这是一个几乎用不到的特性，并且产生一些
  令人困惑的表现。
- 已加入支持每个包模版和静态文件目录。
- 删除 `create_jinja_loader` 的支持，因为在 0.5 中不再使用是为了提升模块支持。
- 已加入一个助手函数来曝露任何一个目录中的文件。

版本 0.4
-----------

发布于 June 18th 2010，代号 Rakia 果酒

- 已加入一项能力，从模块注册应用范围错误处理器。
- :meth:`~flask.Flask.after_request` 方法处理器现在也都开始介入，
  如果请求因为一个列外而终止，然后一个错误处理页面就会出现。
- 测试客户端具有了保留一小段时间的请求语境能力。这项能力也可以用来触发
  为测试而无法删除请求堆栈的自定义请求。
- 由于 Python 标准库缓存日志，日志名现在可以配置成更好地支持单元测试。
- 已加入 ``TESTING`` 开关，它可以激活单元测试助手。
- 如果调试模式开启的话，日志现在可以切换到 ``DEBUG`` 调试模式。

版本 0.3.1
-------------

Bug 修复，发布于 May 28th 2010

- 修复了一个使用 :meth:`flask.Config.from_envvar` 方法报告时产生的一个错误。
- 删除了一些 flask 中未使用的代码。
- 本版本中不再含有开发残留文件 ( 对于主题来说的 .git 文件夹，建立文档时产生的 zip
  和 pdf 文件，以及一些 .pyc 文件)

版本 0.3
-----------

发布于 May 28th 2010，代号 Schnaps 白酒

- 已加入对闪存消息分类的支持。
- 现在应用程序配置了一个 :class:`logging.Handler` 类并且在没有开启
  调试模式时把那些请求处理例外错误记录在日志中。例如，这样可能实现接收
  到服务器错误方面的电子邮件通知。
- 已加入支持语境绑定，语境绑定不需要在终端里使用 ``with`` 语句。
- 现在请求语境可以用在 ``with`` 语句里了，这样做可以实现稍后推送请求语境，
  或者删除请求语境。
- 已加入支持许多配置。

版本 0.2
-----------

发布于 May 12th 2010，代号 Jägermeister 开胃酒

- 各种 bug 修复
- 集成了 JSON 支持
- 已加入 :func:`~flask.get_template_attribute` 助手函数。
- :meth:`~flask.Flask.add_url_rule` 该方法现在也可以注册
  一个视图函数了。
- 重构内部请求调度。
- 修复了使用 chrome 浏览器默认访问在 127.0.0.1 上的服务器问题。
- 已加入支持外部 URL 功能。
- 已加入 :func:`~flask.send_file` 函数的支持。
- 模块支持与内部请求处理重构成更好地支援可插拔应用程序。
- 在每个会话基础上现在可以把会话设置成永久的了。
- 在缺少密钥情况下有更好的错误报告内容。
- 已加入支持 Google Appengine 应用引擎。

版本 0.1
-----------

第一次公开预览发布。
