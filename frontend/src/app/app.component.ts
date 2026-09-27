import { Component, HostListener, Input, ViewChild } from '@angular/core';
import { SearchBarComponent } from './search-bar/search-bar.component';
import { PostcodeService } from './services/postcode.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  @ViewChild('searchBar') searchBar!: SearchBarComponent;
  title = 'frontend';
  markdownResponse = '';
  ngOnInit(): void {}

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
  console.log('Backend response:', response);

  try {
    // HttpClient already parsed the wrapper, we just parse the inner string
    const payload = JSON.parse(response.markdown);
    this.markdownResponse = payload.markdown || '';
  } catch (error) {
    console.error('Failed to parse inner markdown string:', error);
    this.markdownResponse = '';
  }

  if (this.markdownResponse) {
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
