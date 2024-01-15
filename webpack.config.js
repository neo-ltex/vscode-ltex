//@ts-check

'use strict';

const Path = require('path');

/**@type {import('webpack').Configuration}*/
const config = {
  target: 'node',
  mode: 'development',
  entry: './src/extension.ts',
  output: {
    path: Path.resolve(__dirname, 'dist'),
    filename: 'extension.js',
    libraryTarget: 'commonjs2',
    devtoolModuleFilenameTemplate: '../[resource-path]',
  },
  devtool: 'source-map',
  externals: {
    'coc.nvim': 'commonjs coc.nvim',
    vscode: 'commonjs vscode',
  },
  resolve: {
    extensions: [
      '.ts',
      '.js',
    ],
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader'
          },
        ],
      },
    ],
  },
  optimization: {
    minimizer: [
      () => ({
        terserOptions: {
          extractComments: false,
        },
      }),
    ],
  },
};

module.exports = config;
