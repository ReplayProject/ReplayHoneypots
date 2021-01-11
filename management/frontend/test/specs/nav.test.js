var assert = require('assert');
const BASE = 'https://localhost:8443'

//This test suite tests the navigation bar and basic object management and makes sure they are functional
describe('Test Navigation', () => {
    const { Builder, By, until, Capabilities, Capability } = require('selenium-webdriver');
    var driver;
    const capabilities = Capabilities.chrome();
    capabilities.setPageLoadStrategy('normal');
    capabilities.set(Capability.ACCEPT_INSECURE_TLS_CERTS, true);

    before(() => {
        driver = new Builder()
            .withCapabilities(capabilities)
            .forBrowser('chrome')
            .build();
    });

    after(() => {
        driver.quit();
    });

    it('testUserProfile', async () => {
        await driver.get(BASE);
        await driver.findElement(By.name('username')).sendKeys('admin');
        await driver.findElement(By.name('password')).sendKeys('admin');
        await driver.findElement(By.name('btnSignIn')).click();
        await driver.wait(until.urlIs('https://localhost:8443/'), 5000);
        await driver.findElement(By.linkText("My Profile")).click();
        await driver.wait(until.urlIs('https://localhost:8443/users/userAdminDefault'), 10000);

        await driver.wait(until.elementsLocated(By.name('username')));
        await driver.findElement(By.name('username')).getAttribute("value").then(textValue => {
            console.log(textValue);
            assert.strictEqual("admin", textValue);
        });
        await driver.findElement(By.name('localEnabled')).getAttribute("value").then(textValue => {
            console.log(textValue);
            assert.strictEqual('true', textValue);
        });
        await driver.findElement(By.name('firstname')).getAttribute("value").then(textValue => {
            console.log(textValue);
            assert.strictEqual("Phil", textValue);
        });
        await driver.findElement(By.name('lastname')).getAttribute("value").then(textValue => {
            console.log(textValue);
            assert.strictEqual("Lanthripist", textValue);
        });
        await driver.findElement(By.xpath("//*[text()[contains(.,'Cannot delete your own user!')]]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Cannot delete your own user!', textValue);
        })

    }).timeout(10000);

    it('testAdminDisable', async () => {
        await driver.findElement(By.name('localEnabled')).sendKeys('false');
        await driver.findElement(By.name('localEnabled')).getAttribute("value").then(textValue => {
            console.log(textValue);
            assert.strictEqual('false', textValue);
        });
        await driver.findElement(By.xpath("//*[text()[contains(.,'Form is not valid!')]]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Form is not valid!', textValue);
        })
    }).timeout(10000);

    it('testAdminNameChange', async () => {
        await driver.findElement(By.name('firstname')).clear();
        await driver.findElement(By.name('firstname')).sendKeys('testFirstName');
        await driver.findElement(By.name('lastname')).clear();
        await driver.findElement(By.name('lastname')).sendKeys('testLastName');
        await driver.findElement(By.name('localEnabled')).sendKeys('true');
        
        await driver.findElement(By.name('btnUpdateUser')).click();

        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'testFirstName')]")));
        await driver.findElement(By.xpath("//*[text()[contains(.,'testFirstName')]]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('testFirstName', textValue);
        })
        await driver.findElement(By.xpath("//*[text()[contains(.,'testLastName')]]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('testLastName', textValue);
        })

        await driver.findElement(By.linkText("My Profile")).click();
        await driver.wait(until.elementsLocated(By.name('username')));

        await driver.findElement(By.name('firstname')).clear();
        await driver.findElement(By.name('firstname')).sendKeys('Phil');
        await driver.findElement(By.name('lastname')).clear();
        await driver.findElement(By.name('lastname')).sendKeys('Lanthripist');
        await driver.findElement(By.name('btnUpdateUser')).click();

    }).timeout(10000);

    it('testHomePage', async () => {
        await driver.findElement(By.linkText("Home")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'General Stats')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'General Stats')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('General Stats', textValue);
        })
    }).timeout(10000);

    it('testTrafficLogs', async () => {
        await driver.findElement(By.linkText("About")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Traffic at a Glance')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Traffic at a Glance')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Traffic at a Glance', textValue);
        })
    }).timeout(20000);

    it('testUsersPage', async () => {
        await driver.findElement(By.linkText("Users")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'User Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'User Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('User Management', textValue);
        })
    }).timeout(20000);

    it('testAddNewUser', async () => {
        await driver.findElement(By.linkText("Add New User")).click();
        await driver.wait(until.elementsLocated(By.name('localEnabled')), 10000);

        await driver.findElement(By.name('localEnabled')).sendKeys('true');
        await driver.findElement(By.name('username')).sendKeys('testUser');
        await driver.findElement(By.name('firstname')).sendKeys('test');
        await driver.findElement(By.name('lastname')).sendKeys('User');
        await driver.findElement(By.name('password')).sendKeys('test');
        await driver.findElement(By.name('onetimepassword')).sendKeys('true');
        await driver.findElement(By.name('roles')).sendKeys('auditorDefault');
        await driver.findElement(By.name('local')).sendKeys('true');
        await driver.findElement(By.name('addUser')).click();

        await driver.wait(until.elementLocated(By.xpath("//*[contains(text(),'User Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'User Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('User Management', textValue);
        })

        await driver.wait(until.elementLocated(By.xpath("//*[contains(text(),'testUser')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'testUser')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('testUser', textValue);
        })

    }).timeout(10000);

    it('testDeleteUser', async () => {
        await driver.findElement(By.xpath('//*[@id="dashboard"]/div[1]/main/div/div/div/div[3]/table/tbody/tr[5]/td[7]/span/button')).click();
        await driver.wait(until.elementsLocated(By.name('localEnabled')));
        await driver.findElement(By.name('btnDeleteUser')).click();

        await driver.findElement(By.linkText("Users")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'User Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'User Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('User Management', textValue);
        })

    }).timeout(10000);

    it('testRolesPage', async () => {
        await driver.findElement(By.linkText("Roles")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Roles Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Roles Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Roles Management', textValue);
        })
    }).timeout(20000);

    it('testAddNewRole', async () => {
        await driver.findElement(By.linkText("Add New Role")).click();
        await driver.wait(until.elementsLocated(By.name('name')));
        await driver.findElement(By.name('name')).sendKeys('testRole');
        await driver.findElement(By.name('users')).sendKeys('Write');
        await driver.findElement(By.name('roles')).sendKeys('Write');
        await driver.findElement(By.name('adminLogs')).sendKeys('Write');
        await driver.findElement(By.name('traffLogs')).sendKeys('Write');
        await driver.findElement(By.name('devices')).sendKeys('Write');
        await driver.findElement(By.name('metrics')).sendKeys('Write');
        await driver.findElement(By.name('authGroups')).sendKeys('Write');
        await driver.findElement(By.name('alerts')).sendKeys('Write');
        await driver.findElement(By.name('configs')).sendKeys('Write');
        await driver.findElement(By.name('assignAuthGroup')).sendKeys('authGroupDefault');
        await driver.findElement(By.name('authAccessLevel')).sendKeys('None');
        await driver.findElement(By.name('btnAddAuth')).click();
        await driver.findElement(By.name('btnAddRole')).click();

        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'testRole')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'testRole')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('testRole', textValue);
        })

    }).timeout(10000);

    it('testAddDuplicateRole', async () => {
        await driver.findElement(By.linkText("Add New Role")).click();
        await driver.wait(until.elementsLocated(By.name('name')));
        await driver.findElement(By.name('name')).sendKeys('testRole');
        await driver.findElement(By.name('users')).sendKeys('Write');
        await driver.findElement(By.name('roles')).sendKeys('Write');
        await driver.findElement(By.name('adminLogs')).sendKeys('Write');
        await driver.findElement(By.name('traffLogs')).sendKeys('Write');
        await driver.findElement(By.name('devices')).sendKeys('Write');
        await driver.findElement(By.name('metrics')).sendKeys('Write');
        await driver.findElement(By.name('authGroups')).sendKeys('Write');
        await driver.findElement(By.name('alerts')).sendKeys('Write');
        await driver.findElement(By.name('configs')).sendKeys('Write');
        await driver.findElement(By.name('assignAuthGroup')).sendKeys('authGroupDefault');
        await driver.findElement(By.name('authAccessLevel')).sendKeys('None');
        await driver.findElement(By.name('btnAddAuth')).click();
        await driver.findElement(By.name('btnAddRole')).click();

        //Should stay on same page
        await driver.findElement(By.xpath("//*[contains(text(),'Add New Role')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Add New Role', textValue);
        })
    }).timeout(10000);

    it('testDeleteRole', async () => {
        await driver.findElement(By.linkText("Roles")).click();
        await driver.wait(until.elementsLocated(By.xpath('//*[@id="dashboard"]/div[1]/main/div/div/div/div[3]/table/tbody/tr[5]')));
        await driver.findElement(By.xpath('//*[@id="dashboard"]/div[1]/main/div/div/div/div[3]/table/tbody/tr[5]/td[6]/span/button')).click();

        await driver.wait(until.elementsLocated(By.name('users')));
        await driver.findElement(By.name('btnDeleteRole')).click();

        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Roles Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Roles Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Roles Management', textValue);
        })
    }).timeout(10000);

    it('testConfigsPage', async () => {
        await driver.findElement(By.linkText("Configs")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Config Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Config Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Config Management', textValue);
        })
    }).timeout(20000);

    // it('testAddNewConfig', async () => {
    //     //TODO
    // }).timeout(10000);

    // it('testUpdateConfig', async () => {
    //     //TODO
    // }).timeout(10000);

    // it('testDeleteConfig', async () => {
    //     //TODO
    // }).timeout(10000);

    it('testAuthGroupsPage', async () => {
        await driver.findElement(By.linkText("Auth Groups")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Auth Groups Management')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Auth Groups Management')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Auth Groups Management', textValue);
        })
    }).timeout(20000);

    it('testAddAuthGroup', async () => {
        await driver.findElement(By.linkText("Add New Auth Group")).click();
        await driver.wait(until.elementsLocated(By.name('_id')));
        await driver.findElement(By.name('_id')).sendKeys('testAuthGroup');
        await driver.findElement(By.name('btnAddAuthGroup')).click();
        await driver.wait(until.elementLocated(By.xpath("//*[contains(text(),'testAuthGroup')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'testAuthGroup')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('testAuthGroup', textValue);
        })
    }).timeout(10000);

    it('testAddDuplicateAuthGroup', async () => {
        await driver.findElement(By.linkText("Add New Auth Group")).click();
        await driver.wait(until.elementsLocated(By.name('_id')));
        await driver.findElement(By.name('_id')).sendKeys('testAuthGroup');
        await driver.findElement(By.name('btnAddAuthGroup')).click();

        //We stay on the same page
        await driver.findElement(By.xpath("//*[contains(text(),'Add New Auth Group')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Add New Auth Group', textValue);
        })
        
    }).timeout(10000);

    it('testDeleteAuthGroup', async () => {
        await driver.findElement(By.linkText("Auth Groups")).click();
        await driver.wait(until.elementsLocated(By.xpath('//*[@id="dashboard"]/div[1]/main/div/div/div/div[3]/table/tbody/tr[3]/td[2]/span/button')));
        await driver.findElement(By.xpath('//*[@id="dashboard"]/div[1]/main/div/div/div/div[3]/table/tbody/tr[3]/td[2]/span/button')).click();
        await driver.get('https://localhost:8443/authGroups');
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Auth Groups Management')]")));
    }).timeout(10000);

    it('testAdminLogsPage', async () => {
        await driver.findElement(By.linkText("Admin Logs")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Admin Logs')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Admin Logs')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Admin Logs', textValue);
        })
    }).timeout(20000);

    it('testOverviewPage', async () => {
        await driver.findElement(By.linkText("Overview")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'General Stats')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'General Stats')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('General Stats', textValue);
        })
    }).timeout(20000);

    it('testHoneyPotsPage', async () => {
        await driver.findElement(By.linkText("Honeypots")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Honeypots')]")));
    }).timeout(20000);

    it('testMetricsPage', async () => {
        await driver.findElement(By.linkText("Metrics")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Device Metrics')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Device Metrics')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Device Metrics', textValue);
        })
    }).timeout(20000);

    it('testAlertsPage', async () => {
        await driver.findElement(By.linkText("Alerts")).click();
        await driver.wait(until.elementsLocated(By.xpath("//*[contains(text(),'Alerts')]")));
        await driver.findElement(By.xpath("//*[contains(text(),'Alerts')]")).getText().then(textValue => {
            console.log(textValue);
            assert.strictEqual('Alerts', textValue);
        })
    }).timeout(20000);

});
