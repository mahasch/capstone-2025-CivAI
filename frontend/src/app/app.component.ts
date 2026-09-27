import { Component, HostListener, Input, ViewChild } from '@angular/core';
import { SearchBarComponent } from './search-bar/search-bar.component';
import { PostcodeService } from './services/postcode.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  @ViewChild('searchBar') searchBar!: SearchBarComponent;
  title = 'frontend';
  markdownResponse = '';
  ngOnInit(): void {
  
  }
// markDownResponse =  `# Exploring the Wonders of the Universe
// The universe is vast, mysterious, and full of astonishing phenomena. From black holes to nebulae, every corner of space holds secrets waiting to be discovered.
// ---
// ## The Beauty of Nebulae

// Nebulae are massive clouds of gas and dust in space, often serving as stellar nurseries where new stars are born.

// ![Orion Nebula](https://images.unsplash.com/photo-1578898889379-3b0f9b2d2c29?auto=format&fit=crop&w=800&q=80)

// Some famous nebulae include:

// - **Orion Nebula** – One of the brightest nebulae visible to the naked eye.
// - **Crab Nebula** – Remnant of a supernova explosion observed in 1054 AD.
// - **Horsehead Nebula** – Known for its distinct shape resembling a horse’s head.

// ---

// ## Black Holes: Cosmic Enigmas

// Black holes are regions in space where gravity is so strong that nothing, not even light, can escape.

// \`\`\`python
// def schwarzschild_radius(mass):
//     # Calculate radius in meters
//     G = 6.67430e-11
//     c = 299792458
//     return 2 * G * mass / c**2

// mass_sun = 1.989e30
// print(schwarzschild_radius(mass_sun))
// \`\`\`
// `;
  constructor(private postcodeService: PostcodeService) {}
  private hasFocused = false;
  hasEntered = false;
  isLoading = true;

  @HostListener('window:keydown', ['$event'])
  handleKeyDown(event: KeyboardEvent): void {
    if (event.key.length >= 1 && !this.hasFocused) {
      this.hasFocused = true;
      this.searchBar.focusInput();
    }
  }
  onSearchValue(postcode: string): void {
    this.hasEntered = true;
    this.isLoading = true;
    this.postcodeService.sendPostcode(postcode).subscribe({
    next: (response) => {
      console.log('Backend response', response);
      this.markdownResponse = response.markdown;
      if (this.markdownResponse !== '') {
        this.isLoading = false;
      }
    },
    error: (err) => {
      console.error('Backend error', err);
      this.isLoading = false;
    },
  });
    
    // reponse is MD format
  }
}
