var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

import React from 'react';
import ReactDOM from 'react-dom';

var TestAJAX = function (_React$Component) {
    _inherits(TestAJAX, _React$Component);

    function TestAJAX(props) {
        _classCallCheck(this, TestAJAX);

        var _this = _possibleConstructorReturn(this, (TestAJAX.__proto__ || Object.getPrototypeOf(TestAJAX)).call(this, props));

        _this.state = {
            'isLoaded': false,
            'items': []
        };
        return _this;
    }

    _createClass(TestAJAX, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this2 = this;

            fetch("http://127.0.0.1:8000/run_app/get_run_data/").then(function (results) {
                return results.json();
            }).then(function (json) {
                _this2.setState({
                    'isLoaded': true,
                    'items': JSON.parse(json)
                });
            });
        }
    }, {
        key: 'render',
        value: function render() {
            var _state = this.state,
                isLoaded = _state.isLoaded,
                items = _state.items;

            if (!isLoaded) {
                return React.createElement(
                    'h5',
                    { key: 'load' },
                    'Loading.....'
                );
            } else {
                return React.createElement(
                    'table',
                    { className: 'table' },
                    React.createElement(
                        'thead',
                        null,
                        React.createElement(
                            'tr',
                            null,
                            React.createElement(
                                'th',
                                null,
                                'Date'
                            ),
                            React.createElement(
                                'th',
                                null,
                                'Distance'
                            ),
                            React.createElement(
                                'th',
                                null,
                                'Time'
                            ),
                            React.createElement(
                                'th',
                                null,
                                'Calories'
                            )
                        )
                    ),
                    React.createElement(
                        'tbody',
                        null,
                        items.map(function (item) {
                            return React.createElement(
                                'tr',
                                { key: item.date },
                                React.createElement(
                                    'td',
                                    null,
                                    item.date
                                ),
                                React.createElement(
                                    'td',
                                    null,
                                    item.distance
                                ),
                                React.createElement(
                                    'td',
                                    null,
                                    item.time
                                ),
                                React.createElement(
                                    'td',
                                    null,
                                    item.calories
                                )
                            );
                        })
                    )
                );
            }
        }
    }]);

    return TestAJAX;
}(React.Component);

ReactDOM.render(React.createElement(TestAJAX, null), document.getElementById('root'));