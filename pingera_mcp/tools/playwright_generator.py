
"""
MCP tools for generating Playwright scripts.
"""
import json
from typing import Optional

from .base import BaseTools
from ..exceptions import PingeraError


class PlaywrightGeneratorTools(BaseTools):
    """Tools for generating Playwright scripts for monitoring checks."""

    async def generate_synthetic_check_script(self, description: str, target_url: str, script_name: Optional[str] = None) -> str:
        """
        Generate a Playwright script for synthetic browser monitoring.
        
        Args:
            description: Natural language description of what the test should do
            target_url: The URL to test
            script_name: Optional name for the test (auto-generated if not provided)
            
        Returns:
            JSON string with generated Playwright script
        """
        try:
            self.logger.info(f"Generating synthetic check script for: {description}")

            # Auto-generate script name if not provided
            if not script_name:
                script_name = f"Synthetic Check - {target_url}"

            # Generate the Playwright script based on description
            script_content = self._generate_browser_script(description, target_url, script_name)

            return self._success_response({
                "script_name": script_name,
                "script_type": "synthetic_browser_check",
                "target_url": target_url,
                "description": description,
                "script_content": script_content,
                "instructions": {
                    "usage": "Save this script as a .js file and run with: npx playwright test script.js",
                    "requirements": "Requires @playwright/test package: npm install -D @playwright/test",
                    "configuration": "Configure Playwright with: npx playwright install"
                }
            })

        except Exception as e:
            self.logger.error(f"Error generating synthetic check script: {e}")
            return self._error_response(str(e))

    async def generate_api_check_script(self, description: str, base_url: str, script_name: Optional[str] = None) -> str:
        """
        Generate a Playwright script for multi-step API monitoring.
        
        Args:
            description: Natural language description of the API test flow
            base_url: The base API URL to test
            script_name: Optional name for the test (auto-generated if not provided)
            
        Returns:
            JSON string with generated Playwright script
        """
        try:
            self.logger.info(f"Generating API check script for: {description}")

            # Auto-generate script name if not provided
            if not script_name:
                script_name = f"API Check - {base_url}"

            # Generate the Playwright API script based on description
            script_content = self._generate_api_script(description, base_url, script_name)

            return self._success_response({
                "script_name": script_name,
                "script_type": "api_check",
                "base_url": base_url,
                "description": description,
                "script_content": script_content,
                "instructions": {
                    "usage": "Save this script as a .js file and run with: npx playwright test script.js",
                    "requirements": "Requires @playwright/test package: npm install -D @playwright/test",
                    "configuration": "Configure Playwright with: npx playwright install"
                }
            })

        except Exception as e:
            self.logger.error(f"Error generating API check script: {e}")
            return self._error_response(str(e))

    def _generate_browser_script(self, description: str, target_url: str, script_name: str) -> str:
        """Generate a browser automation Playwright script based on description."""
        
        # Create the basic script structure
        script = f'''const {{ test, expect }} = require('@playwright/test');

test('{script_name}', async ({{ page }}) => {{
  // {description}
  
  // Set viewport size for consistent testing
  await page.setViewportSize({{ width: 1280, height: 720 }});
  
  console.log('Starting test: {script_name}');
  
  try {{
    // Navigate to the target URL
    console.log('Navigating to: {target_url}');
    await page.goto('{target_url}');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
    console.log('Page loaded successfully');
    
    // Take a screenshot for verification
    await page.screenshot({{ path: 'screenshot.png', fullPage: false }});
    console.log('Screenshot captured');
    
    // Basic page validation
    await expect(page).toHaveTitle(/.+/); // Page should have a title
    console.log('Page title validation passed');
    
    // TODO: Add specific test steps based on your requirements
    // Examples of common test actions:
    
    // Wait for specific element to be visible
    // await page.waitForSelector('your-selector', {{ state: 'visible' }});
    
    // Click on elements
    // await page.click('button[type="submit"]');
    
    // Fill form fields
    // await page.fill('input[name="username"]', 'testuser');
    // await page.fill('input[name="password"]', 'testpass');
    
    // Check for text content
    // await expect(page.locator('h1')).toContainText('Expected Text');
    
    // Validate page responses
    // const response = await page.waitForResponse('**/api/endpoint');
    // expect(response.status()).toBe(200);
    
    console.log('Test completed successfully');
    
  }} catch (error) {{
    console.error('Test failed:', error.message);
    
    // Take screenshot on failure for debugging
    await page.screenshot({{ path: 'error-screenshot.png', fullPage: true }});
    
    throw error;
  }}
}});'''

        return script

    def _generate_api_script(self, description: str, base_url: str, script_name: str) -> str:
        """Generate an API testing Playwright script based on description."""
        
        script = f'''const {{ test, expect }} = require('@playwright/test');

const baseUrl = "{base_url}";

test('{script_name}', async ({{ request }}) => {{
  // {description}
  
  console.log('Starting API test: {script_name}');
  console.log('Base URL:', baseUrl);
  
  try {{
    // TODO: Customize these API calls based on your specific requirements
    
    // Example: Health check or basic GET request
    console.log('Performing health check...');
    const healthResponse = await request.get(`${{baseUrl}}/health`);
    expect(healthResponse.status()).toBe(200);
    console.log('Health check passed');
    
    // Example: Authentication (if required)
    // console.log('Authenticating...');
    // const authResponse = await request.post(`${{baseUrl}}/auth/login`, {{
    //   data: {{
    //     username: 'testuser',
    //     password: 'testpass'
    //   }}
    // }});
    // expect(authResponse.status()).toBe(200);
    // const authData = await authResponse.json();
    // const token = authData.token;
    // console.log('Authentication successful');
    
    // Example: Authenticated API call
    // console.log('Making authenticated API call...');
    // const dataResponse = await request.get(`${{baseUrl}}/api/data`, {{
    //   headers: {{
    //     'Authorization': `Bearer ${{token}}`
    //   }}
    // }});
    // expect(dataResponse.status()).toBe(200);
    // const data = await dataResponse.json();
    // expect(data).toHaveProperty('results');
    // console.log('API call successful, received data:', data);
    
    // Example: POST request with data validation
    // console.log('Creating new resource...');
    // const createResponse = await request.post(`${{baseUrl}}/api/resources`, {{
    //   data: {{
    //     name: 'Test Resource',
    //     type: 'test'
    //   }},
    //   headers: {{
    //     'Authorization': `Bearer ${{token}}`,
    //     'Content-Type': 'application/json'
    //   }}
    // }});
    // expect(createResponse.status()).toBe(201);
    // const newResource = await createResponse.json();
    // expect(newResource).toHaveProperty('id');
    // console.log('Resource created successfully:', newResource);
    
    // Example: Validate response time
    // const startTime = Date.now();
    // const perfResponse = await request.get(`${{baseUrl}}/api/performance-test`);
    // const endTime = Date.now();
    // const responseTime = endTime - startTime;
    // expect(responseTime).toBeLessThan(2000); // Should respond within 2 seconds
    // console.log(`Response time: ${{responseTime}}ms`);
    
    console.log('All API tests completed successfully');
    
  }} catch (error) {{
    console.error('API test failed:', error.message);
    
    // Log additional debugging information
    if (error.response) {{
      console.error('Response status:', error.response.status());
      console.error('Response body:', await error.response.text());
    }}
    
    throw error;
  }}
}});'''

        return script
