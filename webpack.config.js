const path = require('path');

module.exports = {
  entry: './src/main.js', // or wherever your main.js is located
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
  mode: 'development',
};
