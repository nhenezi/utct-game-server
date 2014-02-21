(function() {
  var MongoStore, RedisStore, Store, mongo, redis,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  mongo = require('mongodb');

  redis = require('redis');

  Store = (function() {

    Store.init = function(config) {
      switch (config.type) {
        case "mongodb":
          return new MongoStore(config);
        case "redis":
          return new RedisStore(config);
        default:
          throw new Error('Invalid Storage Type');
      }
    };

    function Store(config) {
      this.config = config;
    }

    Store.prototype.connect = function(next) {
      throw new Error('must override');
    };

    Store.prototype.insert = function(room, event, data) {
      throw new Error('must override');
    };

    Store.prototype.listen = function(next) {
      throw new Error('must override');
    };

    return Store;

  })();

  MongoStore = (function(_super) {

    __extends(MongoStore, _super);

    function MongoStore() {
      MongoStore.__super__.constructor.apply(this, arguments);
    }

    MongoStore.prototype.connect = function(next) {
      var db, server, _base, _base2, _base3,
        _this = this;
      if (this.collection) return next();
      if ((_base = this.config).collection == null) _base.collection = 'events';
      if ((_base2 = this.config).host == null) _base2.host = 'localhost';
      if ((_base3 = this.config).port == null) _base3.port = 27017;
      server = new mongo.Server(this.config.host, this.config.port, {
        auto_reconnect: true
      });
      db = new mongo.Db(this.config.database, server);
      return db.open(function(err, client) {
        if (err) throw err;
        if (_this.config.username && _this.config.password) {
          client.authenticate(_this.config.username, _this.config.password, function(err) {
            if (err) throw err;
            _this.collection = new mongo.Collection(client, _this.config.collection);
            return next();
          });
        } else {

        }
        _this.collection = new mongo.Collection(client, _this.config.collection);
        return next();
      });
    };

    MongoStore.prototype.insert = function(room, event, data) {
      var _this = this;
      return this.connect(function() {
        return _this.collection.insert({
          room: room,
          event: event,
          data: data
        }, function(err) {
          if (err) throw err;
        });
      });
    };

    MongoStore.prototype.listen = function(next) {
      var _this = this;
      return this.connect(function() {
        var cursor, stream;
        cursor = _this.collection.find({}, {
          tailable: true
        });
        stream = cursor.stream();
        return stream.on('data', function(doc) {
          return next(doc.room, doc.event, doc.data);
        });
      });
    };

    return MongoStore;

  })(Store);

  RedisStore = (function(_super) {

    __extends(RedisStore, _super);

    function RedisStore() {
      RedisStore.__super__.constructor.apply(this, arguments);
    }

    RedisStore.prototype.connect = function(next) {
      var _base, _base2, _base3;
      if (this.client) return next();
      if ((_base = this.config).channel == null) _base.channel = 'pubsub';
      if ((_base2 = this.config).host == null) _base2.host = 'localhost';
      if ((_base3 = this.config).port == null) _base3.port = 6379;
      this.client = redis.createClient(this.config.port, this.config.host);
      if (this.config.password) {
        return this.client.auth(this.config.password, next);
      } else {
        return next();
      }
    };

    RedisStore.prototype.insert = function(room, event, doc) {
      var _this = this;
      return this.connect(function() {
        var data;
        data = {
          room: room,
          event: event,
          doc: doc
        };
        return _this.client.publish(_this.config.channel, JSON.stringify(data));
      });
    };

    RedisStore.prototype.listen = function(next) {
      var _this = this;
      return this.connect(function() {
        _this.client.subscribe(_this.config.channel);
        return _this.client.on('message', function(channel, data) {
          data = JSON.parse(data);
          return next(data.room, data.event, data.doc);
        });
      });
    };

    return RedisStore;

  })(Store);

  exports.middleware = function(config) {
    var store;
    store = Store.init(config);
    return function(req, res, next) {
      req.publish = function(room, event, data) {
        return store.insert(room, event, data);
      };
      return next();
    };
  };

  exports.listen = function(sockets, config) {
    var store;
    store = Store.init(config);
    return store.listen(function(room, event, data) {
      return sockets["in"](room).emit(event, data);
    });
  };

}).call(this);
