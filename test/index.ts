/* Copyright (C) 2019-2021 Julian Valentin, LTeX Development Community
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import { glob } from 'glob'
import Mocha from 'mocha'
import * as Path from 'path'

export function run(): Promise<void> {
  const mocha: Mocha = new Mocha({
    ui: 'bdd',
    timeout: 300000,
    color: true,
  })

  const testsRoot: string = Path.resolve(__dirname, '..')

  return glob('**/**.test.js', { cwd: testsRoot }).then(files => {
    files.forEach((x: string) => mocha.addFile(Path.resolve(testsRoot, x)))

    try {
      return new Promise((a, r) => {
        mocha.run((failures: number): void => {
          if (failures > 0) {
            r(new Error(`${failures} tests failed.`))
          } else {
            a()
          }
        })
      })
    } catch (e: unknown) {
      console.error(e)
      throw e
    }
  })
}
