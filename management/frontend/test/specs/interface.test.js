var webdriver = require('selenium-webdriver');
let chrome = require('selenium-webdriver/chrome')

var assert = require('assert');
const BASE = 'https://localhost:8443'

describe('Test Login', () => {
    //Every test gets 10 seconds before timeout
    const { Builder, By, until, Capabilities, Capability } = require('selenium-webdriver');
    var driver;
    const capabilities = Capabilities.chrome();
    capabilities.setPageLoadStrategy('normal');
    capabilities.set(Capability.ACCEPT_INSECURE_TLS_CERTS, true);

    beforeEach(() => {
        driver = new Builder()
            .withCapabilities(capabilities)
            .forBrowser('chrome')
            .build();
    });

    after(() => {
        driver.quit();
    });

    it('should login with valid login', async () => {
        await driver.get(BASE);
        await driver.findElement(By.name('username')).sendKeys('admin');
        await driver.findElement(By.name('password')).sendKeys('admin');
        await driver.findElement(By.name('btnSignIn')).click();
        await driver.wait(until.urlIs('https://localhost:8443/'), 5000);
        await driver.findElement(By.xpath("//*[contains(text(),'General Stats')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('General Stats', textValue);
        })
    }).timeout(10000);

    it('should reject with invalid login', async () => {
        await driver.get(BASE);
        await driver.findElement(By.name('username')).sendKeys('blah');
        await driver.findElement(By.name('password')).sendKeys('blah');
        await driver.findElement(By.name('btnSignIn')).click();
        await driver.findElement(By.xpath("//*[contains(text(),'Login')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Login', textValue);
        })
    }).timeout(20000);

    it('should log out when prompted', async () => {
        await driver.get(BASE);
        await driver.findElement(By.name('username')).sendKeys('admin');
        await driver.findElement(By.name('password')).sendKeys('admin');
        await driver.findElement(By.name('btnSignIn')).click();
        await driver.wait(until.urlIs('https://localhost:8443/'), 5000);
        await driver.findElement(By.name("logoutClick")).click();
        await driver.wait(until.urlIs('https://localhost:8443/login'), 5000);
        await driver.findElement(By.xpath("//*[contains(text(),'Login')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Login', textValue);
        })
    }).timeout(20000);

});
